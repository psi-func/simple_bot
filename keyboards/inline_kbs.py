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
