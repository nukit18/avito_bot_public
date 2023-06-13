from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def keyboard_urls_remove(links):
    keyboard_urls = InlineKeyboardMarkup(resize_keyboard=True)
    for link in links:
        keyboard_urls.add(InlineKeyboardButton(text=link.name, callback_data=link.name))
    keyboard_urls.add(InlineKeyboardButton(text="Отменить", callback_data="cancel_remove"))
    return keyboard_urls