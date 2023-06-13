from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_link_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, верно", callback_data="yes_newlink")
            ],
            [
                InlineKeyboardButton(text="Нет, изменить", callback_data="no_newlink")
            ],
            [
                InlineKeyboardButton(text="Отменить", callback_data="cancel")
            ]
        ]
    )