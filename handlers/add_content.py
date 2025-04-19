from email.policy import default
import re

import asyncio
from venv import logger
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from create_bot import bot, admins, pg_db
from filters.is_admin import IsAdmin
from keyboards.inline_kbs import add_content_kb

add_content_router = Router()


class AddContent(StatesGroup):
    intro = State()
    content = State()


def extract_number(text):
    match = re.search(r"\b(\d+)\b", text)
    if match:
        return int(match.group(1))
    else:
        return None


@add_content_router.message(Command("add_daily_content"), IsAdmin(admins))
async def start_adding_daily_program(
    message: Message, command: CommandObject, state: FSMContext
):
    if command.args is None:
        await message.reply(
            "Пожалуйста, добавь к команде корректный день (число от 1 до 300)."
        )
        return

    command_args: str = command.args
    check_day = extract_number(command_args)

    if not check_day or not (1 <= check_day <= 300):
        await message.reply("Пожалуйста, введите корректный день число от 1 до 300.")
        return

    await state.clear()
    await state.update_data(day=check_day)

    START_MESSAGE = f"""Добавляем/Изменяем контент на {check_day} день
Жду интро-сообщение:"""
    await message.answer(START_MESSAGE, reply_markup=add_content_kb())
    await state.set_state(AddContent.intro)


@add_content_router.callback_query(F.data.startswith("add_daily_content_"))
async def mod_pipeline(call: CallbackQuery, state: FSMContext):
    cur_state = await state.get_state()
    chat_id = call.message.chat.id

    if not cur_state.startswith("AddContent:"):
        await call.answer()
        await bot.send_message(
            chat_id=chat_id,
            text="Ты, наверное, перепутал..."
            "Начни заполнение заново с помощью команды /add_daily_content",
        )
        return

    req = call.data.replace("add_daily_content_", "")
    if req == "reset":
        await call.answer()
        await bot.send_message(chat_id=chat_id, text="Снова жду от тебя интро:")
        data = await state.get_data()
        await state.set_data({"day": data.get("day")})
        await state.set_state(AddContent.intro)
        return
    if req == "done":
        cur_state = await state.get_state()
        logger.info(cur_state)
        if cur_state.endswith("content"):
            await call.answer("Записал, спасибо", show_alert=False)
            await call.message.edit_reply_markup(reply_markup=None)
            # TODO: add DB instance
            data = await state.get_data()
            day = data.get("day")
            # remove old data
            await pg_db.remove_content(day)
            # add intro
            intro = {"text": data.get("intro"), "day_id": day}
            await pg_db.insert_content(intro)

            # add all stuff
            for entry in data.get("content", list()):
                entry["day_id"] = day
                await pg_db.insert_content(entry)
            await state.clear()
            return

        await call.answer("Странно, добавь хотя бы интро", show_alert=False)
        return
    if req == "cancel":
        await call.answer()
        await bot.send_message(chat_id=chat_id, text="Отмена ввода")
        await state.clear()
        await call.message.delete()
        return


@add_content_router.message(F.text, AddContent.intro)
async def get_intro(message: Message, state: FSMContext):
    await state.update_data(intro=message.text)
    await message.answer(
        "Теперь присылайте фотографии, музыку, текст в том порядке, который должен увидеть пользователь"
    )
    await state.set_state(AddContent.content)


@add_content_router.message(AddContent.content)
async def get_post(message: Message, state: FSMContext):
    data = await state.get_data()
    content_lst = data.get("content", list())

    content = dict()

    log = "Добавил: "
    if message.text is not None:
        content["text"] = message.text
        log += "текст "
    if message.photo is not None:
        content["photo"] = message.photo[-1].file_id
        log += f"фото с id {content['photo']} "
    if message.audio is not None:
        content["audio"] = message.audio.file_id
        log += f"аудио запись с id {content['photo']}"

    content_lst.append(content)
    await message.answer(log)
    await state.update_data(content=content_lst)
    await state.set_state(AddContent.content)
