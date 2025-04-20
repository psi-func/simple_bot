from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from create_bot import admins


def common_kb(tg_user_id: int):
    kb_list = [
        [KeyboardButton(text="Пройти программу на день")],
        [KeyboardButton(text="Изменить время рассылки")],
        [KeyboardButton(text="Приостановить рассылку")],
    ]
    if tg_user_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:",
    )
    return keyboard

def add_content_kb():
    kb_list = [
        [KeyboardButton(text="Разделение"), KeyboardButton(text="Готово")],
        [KeyboardButton(text="Начать заново"), KeyboardButton(text="Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True)
