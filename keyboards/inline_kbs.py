from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def continue_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Продолжить", callback_data='agreement_continue')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def agree_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Всё понятно, давай начнём", callback_data='agreement_done')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def add_content_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Готово", callback_data='add_daily_content_done')],
        [InlineKeyboardButton(text="Отмена", callback_data='add_daily_content_cancel')],
        # [InlineKeyboardButton(text="Изменить предыдущий ответ", callback_data='add_daily_content_cancel_last')],
        [InlineKeyboardButton(text="Начать заново", callback_data='add_daily_content_reset')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
