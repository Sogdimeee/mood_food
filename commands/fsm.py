from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from static.config import bot
from static.kb import create_dynamic_kb, cancel_kb, start_kb, create_end_kb
from static.text import *
from commands.ai import ask_ai
from commands.start import start

fsm_router = Router()

class Food(StatesGroup):
    type = State()
    mood = State()
    aim = State()
    calories = State()
    meals = State()
    format = State()
    preferences = State()
    drink_effect = State()
    drink_base = State()
    done = State()

@fsm_router.callback_query(F.data == "cancel")
async def cancel_process(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Подбор еды приостановлен ❌")
    await start(call.message)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(F.data == "Назад в меню")
async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    photo = types.FSInputFile("images/image.png")
    await call.message.answer_photo(photo=photo, caption=start_text, reply_markup=start_kb)

@fsm_router.callback_query(F.data == "start_fsm")
async def start_fsm(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Food.type)
    await call.message.answer("Давай начнем! Что ты хочешь получить?", reply_markup=create_dynamic_kb(food_type))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.type)
async def choose_type(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(type=choice)

    if choice == "Полный рацион на день":
        await state.set_state(Food.mood)
        await call.message.answer("Выбери свое настроение:", reply_markup=create_dynamic_kb(mood))
    else:
        await state.set_state(Food.format)
        await call.message.answer("Какой формат еды вам удобнее?", reply_markup=create_dynamic_kb(format))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.format)
async def choose_format(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(format=choice)
    await state.set_state(Food.mood)
    await call.message.answer("Выбери свое настроение:", reply_markup=create_dynamic_kb(mood))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.mood)
async def choose_mood(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(mood=choice)

    data = await state.get_data()
    if data.get("type") == "Полный рацион на день":
        await state.set_state(Food.aim)
        await call.message.answer("Какая у тебя цель?", reply_markup=create_dynamic_kb(aim))
    else:
        await state.set_state(Food.aim)
        await call.message.answer("Какая у тебя цель?", reply_markup=create_dynamic_kb(aim))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.aim)
async def choose_aim(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(aim=choice)

    data = await state.get_data()
    if data.get("type") == "Полный рацион на день":
        await state.set_state(Food.calories)
        await call.message.answer("Сколько калорий тебе нужно?", reply_markup=create_dynamic_kb(calories))
    elif data.get("format") in ["Быстрый перекус", "Полноценное блюдо"]:
        await state.set_state(Food.preferences)
        await call.message.answer("Какие у тебя предпочтения?", reply_markup=create_dynamic_kb(preferences))
    elif data.get("format") == "Десерт":
        await finish_with_ai(call, state)
        await bot.delete_message(call.message.chat.id, call.message.message_id
    else:
        await state.set_state(Food.drink_effect)
        await call.message.answer("Какой эффект хочешь от напитка?", reply_markup=create_dynamic_kb(drink_effect))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.calories)
async def choose_calories(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(calories=choice)
    await state.set_state(Food.meals)
    await call.message.answer("Сколько приемов пищи в день?", reply_markup=create_dynamic_kb(meals))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.meals)
async def choose_meals(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(meals=choice)
    await finish_with_ai(call, state)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.preferences)
async def choose_preferences(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(preferences=choice)
    await finish_with_ai(call, state)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.drink_effect)
async def choose_drink_effect(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(drink_effect=choice)
    await state.set_state(Food.drink_base)
    await call.message.answer("Из чего хочешь напиток?", reply_markup=create_dynamic_kb(drink_base))
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@fsm_router.callback_query(Food.drink_base)
async def choose_drink_base(call: types.CallbackQuery, state: FSMContext):
    choice = call.data
    await state.update_data(drink_base=choice)
    await finish_with_ai(call, state)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

async def finish_with_ai(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    # Отправляем ⏳
    loading_message = await call.message.answer("⏳ Подбираем рацион...")

    # Выбираем текст запроса в зависимости от типа
    if user_data.get('type') == "Полный рацион на день":
        prompt = f"""Подбери рацион на основе следующих данных:
Тип: {user_data.get('type')}
Настроение: {user_data.get('mood')}
Цель: {user_data.get('aim')}
Калорийность: {user_data.get('calories')}
Приемы пищи: {user_data.get('meals')}
Формат: {user_data.get('format')}
Предпочтения: {user_data.get('preferences')}
Эффект напитка: {user_data.get('drink_effect')}
Основа напитка: {user_data.get('drink_base')}

Ответ дай в виде краткого рациона с блюдами. Не используй марки и бренды. Напиши по-человечески и по-русски.
"""
    else:
        prompt = f"""Подбери отдельное блюдо на основе следующих данных:
Формат: {user_data.get('format')}
Настроение: {user_data.get('mood')}
Цель: {user_data.get('aim')}
Предпочтения: {user_data.get('preferences')}
Эффект напитка: {user_data.get('drink_effect')}
Основа напитка: {user_data.get('drink_base')}

Напиши:
- Название блюда.
- Список ингредиентов с количествами.
- Пошаговый рецепт приготовления.
Пиши по-человечески и на русском языке. Не используй бренды!
"""

    ai_response = await ask_ai(prompt)
    await state.update_data(last_prompt=prompt)
    await state.set_state(Food.done)

    response = f"🔍 ИИ подобрал тебе рацион на основе:\n\n" \
               f"📌 Тип: {user_data.get('type')}\n" \
               f"📌 Настроение: {user_data.get('mood')}\n" \
               f"📌 Цель: {user_data.get('aim')}\n" \
               f"📌 Формат: {user_data.get('format')}\n" \
               f"📌 Предпочтения: {user_data.get('preferences')}\n" \
               f"📌 Эффект напитка: {user_data.get('drink_effect')}\n" \
               f"📌 Основа: {user_data.get('drink_base')}\n\n" \
               f"🍽️ Результат:\n\n{ai_response}"

    if user_data.get('type') == "Полный рацион на день":
        calories_choice = user_data.get('calories')
        link = ration_links.get(calories_choice)
        if link:
            response += f"\n\n🔗 Подробнее про подходящий рацион: {link}"

    # Удаляем ⏳
    await bot.delete_message(call.message.chat.id, loading_message.message_id)

    await call.message.answer(response, reply_markup=create_end_kb(["Другое блюдо", "Назад в меню"]))
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@fsm_router.callback_query(F.data == "Другое блюдо", Food.done)
async def repeat_dish(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("last_prompt")
    ai_response = await ask_ai(prompt)

    response = f"🍽️ Вот другое блюдо по тем же параметрам:\n\n{ai_response}"
    await call.message.answer(response, reply_markup=create_end_kb(["Другое блюдо", "Назад в меню"]))
    await bot.delete_message(call.message.chat.id, call.message.message_id)
