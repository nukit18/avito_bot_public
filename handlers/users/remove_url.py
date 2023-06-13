from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Command

from keyboards.inline.confirm_link_keyboard import confirm_link_keyboard
from keyboards.inline.keyboard_urls import keyboard_urls_remove
from loader import dp, bot
from utils.db_api import quick_cmd_urls


@dp.message_handler(Command("remove_parse"))
async def remove_parse(message: types.Message, state: FSMContext):
    links = await quick_cmd_urls.get_urls_user(message.from_user.id)
    keyboard = await keyboard_urls_remove(links)
    await message.answer("Выбери ссылку для удаления", reply_markup=keyboard)
    await state.set_state("input_name_remove")


@dp.callback_query_handler(state="input_name_remove")
async def input_name_remove(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    name = call.data
    if name == "cancel_remove":
        await state.reset_data()
        await state.finish()
        await call.answer("Отменяю")
        return
    await quick_cmd_urls.delete_url_user(call.from_user.id, name)
    await bot.send_message(call.from_user.id, "Рассылка удалена")
    await state.reset_data()
    await state.finish()