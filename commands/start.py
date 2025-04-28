from aiogram import Router, types, F
from static.text import start_text, about_bot
from static.config import bot
from static.kb import start_kb,menu_kb
from aiogram.filters import Command

start_router = Router()

@start_router.message(Command("start"))
async def start(message: types.Message):
    photo = types.FSInputFile("images/barni.png")
    await message.answer_photo(photo=photo, caption=start_text, reply_markup=start_kb)


@start_router.callback_query(F.data == "about_bot")
async def about(call: types.CallbackQuery):
    photo = types.FSInputFile("images/bot.png")
    await call.message.answer_photo(photo=photo, caption=about_bot, reply_markup=menu_kb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@start_router.callback_query(F.data == "back_to_menu")
async def about(call: types.CallbackQuery):
    await start(call.message)
    await bot.delete_message(call.message.chat.id, call.message.message_id)