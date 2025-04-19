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

main_router = Router()

async def send_daily_content():
    pass

@main_router.message(F.text.contains("Отписаться"))
async def unsubscribe(message: Message):
    user_id = message.from_user.id
    await pg_db.subscribe_user(user_id, False)
    message.answer("correctly unsubscribed")

@main_router.message(F.text.contains("Подписаться"))
async def subscribe(message: Message):
    user_id = message.from_user.id
    await pg_db.subscribe_user(user_id, True)
    message.answer("correctly unsubscribed")

