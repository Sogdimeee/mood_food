from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, KeyboardButtonRequestUser,
                           KeyboardButtonRequestChat,  ReplyKeyboardMarkup)


start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подобрать мне блюдо", callback_data="start_fsm")
        ],
        [
            InlineKeyboardButton(text="О боте", callback_data="about_bot")
        ]
    ]
)

cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Остановить генирацию еды", callback_data="cancel"),
        ]
    ]
)

menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu"),
        ]
    ]
)


def create_dynamic_kb(options : list):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for i in options:
        button = InlineKeyboardButton(text=f"{i}", callback_data=f"{i}")
        kb.inline_keyboard.append([button])
    button = InlineKeyboardButton(text=f"Вернуться в меню", callback_data=f"cancel")
    kb.inline_keyboard.append([button])
    return kb

def create_end_kb(options : list):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for i in options:
        button = InlineKeyboardButton(text=f"{i}", callback_data=f"{i}")
        kb.inline_keyboard.append([button])
    return kb