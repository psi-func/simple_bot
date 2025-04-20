import re

from aiogram import Router, F
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from create_bot import admins, pg_db
from filters.is_admin import IsAdmin
from keyboards.all_kbs import add_content_kb

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


async def add_separator(state: FSMContext) -> bool:
    data = await state.get_data()
    content_lst: list = data.get("content", list())
    breaks_lst: list = data.get("separators", list())

    last_cntr = data.get("last_counter", 0)
    cur_cntr = len(content_lst)
    delta = cur_cntr - last_cntr

    if delta <= 0:
        return False

    breaks_lst.append(delta)
    await state.update_data({"separators": breaks_lst, "last_counter": cur_cntr})

    return True


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


@add_content_router.message(F.text.lower() == "готово", AddContent.content)
async def cmd_done(message: Message, state: FSMContext):
    await add_separator(state)
    data = await state.get_data()
    day = data.get("day")

    # add activity
    await pg_db.insert_activity(
        {
            "day_id": day,
            "intro": data.get("intro"),
            "script": ",".join(map(str, data.get("separators", list()))),
        }
    )

    # remove old content
    await pg_db.remove_content(day)

    # add all contents
    for entry in data.get("content", list()):
        entry["day_id"] = day
        await pg_db.insert_content(entry)

    await state.clear()
    await message.answer("Добавил контент")


@add_content_router.message(F.text.lower() == "разделение", AddContent.content)
async def cmd_break(message: Message, state: FSMContext):
    is_added = await add_separator(state)
    if is_added:
        await message.answer("Добавил разделитель")
    else:
        await message.answer("Не добавил разделитель, попробуй добавить контент")


@add_content_router.message(F.text.lower() == "начать заново", AddContent.content)
async def cmd_reset(message: Message, state: FSMContext):
    await message.answer("Снова жду от тебя интро:")
    data = await state.get_data()
    await state.set_data({"day": data.get("day")})
    await state.set_state(AddContent.intro)


@add_content_router.message(
    F.text.lower() == "отмена", StateFilter(AddContent.intro, AddContent.content)
)
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена ввода", reply_markup=ReplyKeyboardRemove())


# ТУТ ПОЛУЧЕНИЕ КОНТЕНТА
@add_content_router.message(F.text, AddContent.intro)
async def get_intro(message: Message, state: FSMContext):
    await state.update_data(intro=message.text)
    await message.answer(
        "Теперь присылайте фотографии, музыку, текст в том порядке, который должен увидеть пользователь",
    )
    await state.set_state(AddContent.content)


@add_content_router.message(F.text, AddContent.content)
async def get_text(message: Message, state: FSMContext):
    data = await state.get_data()
    content_lst: list = data.get("content", list())

    content = dict()
    content["text"] = message.text

    content_lst.append(content)
    await message.answer("Добавил текст")
    await state.update_data(content=content_lst)
    await state.set_state(AddContent.content)


@add_content_router.message(F.photo, AddContent.content)
async def get_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    content_lst = data.get("content", list())

    content = dict()
    content["photo"] = message.photo[-1].file_id
    content["text"] = message.caption

    content_lst.append(content)
    await message.answer(
        f"Добавил фотку {content['photo']} с подписью {content['text']}"
    )
    await state.update_data(content=content_lst)
    await state.set_state(AddContent.content)


@add_content_router.message(F.audio, AddContent.content)
async def get_audio(message: Message, state: FSMContext):
    data = await state.get_data()
    content_lst = data.get("content", list())

    content = dict()
    content["audio"] = message.audio.file_id
    content["text"] = message.caption

    content_lst.append(content)
    await message.answer(
        f"Добавил аудио {content['audio']} с подписью {content['text']}"
    )
    await state.update_data(content=content_lst)
    await state.set_state(AddContent.content)
