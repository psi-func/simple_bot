import datetime

import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from create_bot import bot, admins, pg_db
from filters.is_admin import IsAdmin
from keyboards.all_kbs import common_kb
from keyboards.inline_kbs import continue_kb, agree_kb
from content_provider.start_messages import BEFORE_CONTENT, GREET_MESSAGE, HOW_IT_WORKS


class Agreement(StatesGroup):
    continue_start = State()
    get_agreement = State()


start_router = Router()


@start_router.message(CommandStart(), IsAdmin(admins))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    await message.answer("Привет, админ!", reply_markup=common_kb(user_id))


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await pg_db.get_user_data(user_id)
    if user is not None:
        await message.answer(
            "Привет, Вы уже зарегистрированы!", reply_markup=common_kb(user_id)
        )
    else:
        await state.clear()
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            await message.answer(GREET_MESSAGE, reply_markup=continue_kb())
        await state.set_state(Agreement.continue_start)


@start_router.callback_query(F.data == "agreement_continue", Agreement.continue_start)
async def agreement_continue(call: CallbackQuery, state: FSMContext):
    msg = call.message
    await call.answer(show_alert=False)
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)
    async with ChatActionSender.typing(bot=bot, chat_id=msg.chat.id):
        await asyncio.sleep(1)
        await msg.answer(HOW_IT_WORKS)
        await asyncio.sleep(2)
        await msg.answer(BEFORE_CONTENT, reply_markup=agree_kb())
    await state.set_state(Agreement.get_agreement)


@start_router.callback_query(F.data == "agreement_done", Agreement.get_agreement)
async def agreement_done(call: CallbackQuery, state: FSMContext):
    msg = call.message
    try:
        await pg_db.insert_user({"user_id": call.from_user.id, "subscribed": True, "progress": 1, "date_reg" : datetime.datetime.now()})
    except Exception as ex:
        print(ex)
        await msg.answer("Не удалось зарегистрироваться, попробуйте позже")
        await state.set_state(Agreement.get_agreement)
        return

    await call.answer("Вы подписались на обновления", show_alert=True)
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id)
    await state.clear()

@start_router.message(Agreement.continue_start)
async def agreement_fault(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, нажмите кнопку "Продолжить"')
    await state.set_state(Agreement.continue_start)

@start_router.message(Agreement.get_agreement)
async def agreement_fault(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, подтвердите согласие')
    await state.set_state(Agreement.get_agreement)
