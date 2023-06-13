from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Command

from data.config import ADMINS
from keyboards.inline.confirm_link_keyboard import confirm_link_keyboard
from loader import dp, bot
from utils.db_api import quick_cmd_urls


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")


@dp.message_handler(Command("new_parse"))
async def new_parse(message: types.Message, state: FSMContext):
    urls = await quick_cmd_urls.get_urls_user(message.from_user.id)
    if str(message.from_user.id) not in ADMINS and len(urls) != 0:
        await message.answer("Вы не можете добавить больше одной ссылки!")
        return
    await message.answer("Отправь ссылку на поиск")
    await state.set_state("input_link")


@dp.message_handler(state="input_link")
async def input_link(message: types.Message, state: FSMContext):
    if "https://www.avito.ru" != message.text[:20] or not 25 < len(message.text) < 500:
        await message.answer("Проверь, пожалуйста, корректность ссылки и введи ее еще раз")
        await state.set_state("input_link")
        return
    await message.answer(f"Перейди, пожалуйста, по ссылке и проверь ее корректность. Если все верно, то подтверди это.\nСсылка правильная?\n{message.text}", reply_markup=confirm_link_keyboard)
    await state.update_data(url=message.text)
    await state.set_state("confirm_link")


@dp.callback_query_handler(state="confirm_link")
async def confirm_link(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    if call.data == "yes_newlink":
        await bot.send_message(call.from_user.id, "Отлично, придумай название (оно будет присылаться при рассылках)")
        await state.set_state("input_name")
    elif call.data == "no_newlink":
        await bot.send_message(call.from_user.id, "Хорошо, отправь ссылку заново")
        await state.set_state("input_link")
    else:
        await call.answer("Отменяю ввод")
        await state.reset_data()
        await state.finish()


@dp.message_handler(state="input_name")
async def input_name(message: types.Message, state: FSMContext):
    if await quick_cmd_urls.check_name_url(message.from_user.id, message.text):
        await message.answer("Данное имя уже используется, введи новое")
        await state.set_state("input_name")
        return
    data = await state.get_data()
    url = data.get("url")
    await quick_cmd_urls.add_url(url, message.from_user.id, message.text)
    await state.reset_data()
    await state.finish()
    await message.answer("Отлично, поиск добавлен")