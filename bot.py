import json
import random
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from aiogram.client.default import DefaultBotProperties

# Получаем токен из переменных окружения (Railway использует переменные)
API_TOKEN = os.getenv("BOT_TOKEN")

# Настройка бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Загружаем вопросы из JSON-файла
with open("audit_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Состояние пользователей (какой вопрос кому был задан)
user_states = {}

# Команда /start
@dp.message(CommandStart())
async def start(message: types.Message):
    await send_question(message.chat.id)

# Функция для отправки случайного вопроса
async def send_question(chat_id):
    question = random.choice(questions)
    user_states[chat_id] = question
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(question["options"]):
        builder.button(text=f"{chr(65+i)}) {option}", callback_data=str(i))
    builder.adjust(1)
    await bot.send_message(chat_id, question["question"], reply_markup=builder.as_markup())

# Обработка ответа пользователя
@dp.callback_query(F.data)
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected_index = int(callback.data)
    question = user_states.get(user_id)

    if question:
        correct_index = question["correct_option_index"]
        selected_letter = chr(65 + selected_index)
        selected_text = question["options"][selected_index]

        if selected_index == correct_index:
            response = f"✅ <b>To‘g‘ri javob!</b>\nSiz tanladingiz: <b>{selected_letter}) {selected_text}</b>"
        else:
            correct_letter = chr(65 + correct_index)
            correct_text = question["options"][correct_index]
            response = (
                f"❌ <b>Noto‘g‘ri</b>\n"
                f"Siz tanladingiz: <b>{selected_letter}) {selected_text}</b>\n"
                f"To‘g‘ri javob: <b>{correct_letter}) {correct_text}</b>"
            )

        await callback.answer()
        await bot.send_message(user_id, response)
        await send_question(user_id)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
