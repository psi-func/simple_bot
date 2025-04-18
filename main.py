import asyncio
import logging
import os
from datetime import datetime
import aioschedule as schedule
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dotenv import load_dotenv

import keyboards as kb
from content_provider.start_messages import BEFORE_CONTENT, GREET_MESSAGE, HOW_IT_WORKS
# from content_provider.content_provider import get_relaxing_content
import db as database 

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -----  Определение состояний для FSM  -----
class TimePreference(StatesGroup):
    waiting_for_time = State()

# -----  Клавиатуры  -----
# Кнопка "Подписаться" и "Отписаться"


# -----  Обработчики  -----
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    is_subscribed = database.is_user_subscribed(user_id)
    if is_subscribed:
        await message.answer("Привет! Вы уже подписаны", reply_markup=kb.subscribe_kb)
    else:
        await message.answer(GREET_MESSAGE, reply_markup=kb.continue_kb)

@dp.message(lambda message: message.text == "Продолжить")
async def enter_bot(message: types.Message):
    
    user_id = message.from_user.id
    await message.answer(HOW_IT_WORKS)
    await message.answer(BEFORE_CONTENT, reply_markup=kb.lets_go_kb)

@dp.message(lambda message: message.text == "Всё понятно, давай начнём")
async def agreed_bot(message: types.Message):
    user_id = message.from_user.id
    #  начало скрипта!
    await message.answer("День 1. Только кнопка дальше")
    


@dp.message(lambda message: message.text == "Подписаться")
async def subscribe(message: types.Message):
    """Обработчик подписки на рассылку."""
    user_id = message.from_user.id
    database.subscribe_user(user_id)
    await message.answer("Вы успешно подписались на рассылку!", reply_markup=kb.subscribe_kb)

@dp.message(lambda message: message.text == "Отписаться")
async def unsubscribe(message: types.Message):
    """Обработчик отписки от рассылки."""
    user_id = message.from_user.id
    database.unsubscribe_user(user_id)
    await message.answer("Вы отписались от рассылки.", reply_markup=kb.subscribe_kb)

@dp.message(lambda message: message.text == "Изменить время рассылки")
async def change_time_preference(message: types.Message, state: FSMContext):
    """Обработчик для изменения времени рассылки."""
    await message.answer("Пожалуйста, введите желаемое время рассылки в формате ЧЧ:ММ (например, 10:30).")
    await state.set_state(TimePreference.waiting_for_time)



@dp.message(TimePreference.waiting_for_time)
async def process_time_preference(message: types.Message, state: FSMContext):
    """Обработчик для получения и сохранения времени рассылки."""
    time_str = message.text
    try:
        datetime.strptime(time_str, '%H:%M')  # Проверка формата
        user_id = message.from_user.id
        database.set_user_time_preference(user_id, time_str)
        await message.answer(f"Время рассылки изменено на {time_str}.", reply_markup=kb.subscribe_kb)
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат времени. Пожалуйста, введите в формате ЧЧ:ММ (например, 10:30).")


# -----  Функции для рассылки  -----
async def send_relaxing_content(user_id: int):
    """Отправляет контент для релаксации конкретному пользователю."""
    try:
        content = "msg"
        await bot.send_message(user_id, content)
        logging.info(f"Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def scheduled_content_delivery():
    """Рассылает контент для релаксации всем подписанным пользователям."""
    subscribed_users = database.get_all_subscribed_users()
    for user_id in subscribed_users:
        user_time_preference = database.get_user_time_preference(user_id)
        schedule.every().day.at(user_time_preference).do(send_relaxing_content, user_id=user_id) # Планируем отправку для каждого пользователя

# -----  Запуск планировщика  -----
async def scheduler():
    """Запускает планировщик aioschedule."""
    await scheduled_content_delivery() # Первоначальная инициализация рассылки
    while True:
        await schedule.run_pending()
        await asyncio.sleep(60)  # Проверка каждую минуту

# -----  Запуск бота  -----
async def main():
    """Запускает бота и планировщик."""
    asyncio.create_task(scheduler())  # Запускаем планировщик в фоне
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
