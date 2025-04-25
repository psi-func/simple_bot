import asyncio
from venv import logger
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from create_bot import bot, pg_db
from keyboards.inline_kbs import more_kb


class GetContent(StatesGroup):
    getting_pack = State()


main_router = Router()


@main_router.callback_query(F.data == "get_daily_content_more")
async def get_more(call: CallbackQuery, state: FSMContext):
    msg = call.message
    await call.answer()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)
    await send_content_pack(call.from_user.id, state)


@main_router.message(Command("get_daily_content"))
async def cmd_get_daily_content(message: Message, state: FSMContext):
    await get_daily_content(message.from_user.id, state)


async def send_content_pack(user_id, state: FSMContext):
    data = await state.get_data()
    pack_id = data.get("pack_id")
    start_idx = data.get("start_idx")
    script_lst = data.get("script_lst")
    contents = data.get("contents")
    for i in range(script_lst[pack_id] - 1):
        logger.info("Sending {i}")
        await send_content(contents[start_idx + i], user_id)
    await send_content(
        contents[start_idx + script_lst[pack_id] - 1],
        user_id,
        len(contents) > (start_idx + script_lst[pack_id]),
    )

    await state.update_data(
        start_idx=start_idx + script_lst[pack_id], pack_id=pack_id + 1
    )


async def send_content(content: dict, chat_id: int, with_kb: bool = False):
    kb = more_kb() if with_kb else None
    if content["photo"] is not None:
        # send photo
        await bot.send_photo(
            chat_id=chat_id,
            photo=content["photo"],
            caption=content["text"],
            reply_markup=kb,
        )
    elif content["audio"] is not None:
        await bot.send_audio(
            chat_id=chat_id,
            audio=content["audio"],
            caption=content["text"],
            reply_markup=kb,
        )
    else:
        await bot.send_message(chat_id=chat_id, text=content["text"], reply_markup=kb)


async def get_daily_content(user_id: int, state: FSMContext):
    # get user data
    user = await pg_db.get_user_data(user_id)
    if user is None:
        bot.send_message(
            chat_id=user_id, text="Непредвиденная ошибка, Вы не зарегистрированы!"
        )
        return
    day = user["progress"]
    activity = await pg_db.get_daily_activity(day)
    contents = await pg_db.get_daily_contents(day)
    contents = sorted(contents, key=lambda d: d["content_id"])
    script_lst = [int(count) for count in activity["script"].split(",")]

    await bot.send_message(chat_id=user_id, text=activity["intro"])
    await asyncio.sleep(20)

    await state.clear()
    await state.set_state(GetContent.getting_pack)
    await state.update_data(
        pack_id=0, start_idx=0, contents=contents, script_lst=script_lst
    )

    await send_content_pack(user_id, state)
