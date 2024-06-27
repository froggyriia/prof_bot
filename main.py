from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import InputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from quizdata import quiz_data
from env import token, admins, generate_promo_code
import keyboard as kb
bot = Bot(token=token)
dp = Dispatcher()

all_users = dict()
user_info_data = []
user_data = dict()


class UserInfo(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_phone = State()


class Mail(StatesGroup):
    check_promo = State()


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    all_users[message.from_user.username] = message.from_user.id
    await message.answer('Ваше ФИО:')
    await state.set_state(UserInfo.waiting_for_name)


@dp.message(UserInfo.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Ваш возраст:")
    await state.set_state(UserInfo.waiting_for_age)


@dp.message(UserInfo.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Ваш номер телефона:")
    await state.set_state(UserInfo.waiting_for_phone)


@dp.message(UserInfo.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data['full_name']
    age = user_data['age']
    phone = message.text

    user_info_data.append({
        "full_name": full_name,
        "age": age,
        "phone": phone,
        "telegram_id": message.from_user.id,
        "username": message.from_user.username
    })

    await message.answer("Tеперь вы можете начать квиз, введя команду /quiz")
    await state.clear()

@dp.message(Command('quiz'))
async def cmd_start(message: Message):
    all_users[message.from_user.username] = message.from_user.id
    await message.answer('Добро пожаловать в квиз от Центра стратегического планирования карьеры!')
    user_data[message.from_user.id] = {
        "current_question": 0,
        "correct_answers": 0
        }
    await ask_question(message)


async def ask_question(message):
    user_id = message.from_user.id
    user_info = user_data[user_id]
    current_question = user_info["current_question"]
    if current_question < len(quiz_data):
        question_data = quiz_data[current_question]
        question_text = question_data["question"]
        options = question_data["options"]

        keyboard = []
        for option in options:
            keyboard.append([KeyboardButton(text = option)])

        await bot.send_message(
            chat_id=message.chat.id,
            text=question_text,
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Квиз завершен! Правильных ответов {user_info['correct_answers']} из {len(quiz_data)}",
            reply_markup= ReplyKeyboardRemove()
        )
        await  bot.send_message(
            chat_id=message.chat.id,
            text=f"Подписывайся на [телеграм-канал Центра](https://t.me/kembyt), чтобы участвовать в розыгрыше индивидуальной "
                 f"консультации по профориентации или личностным отношениям ",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN

        )
        await  bot.send_message(
            chat_id=message.chat.id,
            text= f"\nА ещё держи промокод на скидку в 10% на любую услугу Центра:\n`{generate_promo_code()}`\n"
                  f"Чтобы использовать его обратитесь к Наталье (Whatsapp: `+79050845654`)",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode= ParseMode.MARKDOWN

        )

        # Clear user data
        user_data.pop(user_id)


@dp.message(Command('check_promo'))
async def check_promo_start(message: Message, state: FSMContext):
    if message.from_user.username in admins:
        await message.answer("Отправь промокод для проверки:")
        await state.set_state(Mail.check_promo)
    else:
        await message.answer("У вас нет прав администратора для использования этой команды")


@dp.message(Command('get_users'))
async def get_users(message: Message):
    if message.from_user.username in admins:
        if not user_info_data:
            await message.answer("No user data available.")
        else:
            user_info = "ФИО | Возраст | Номер телефона | Username\n"
            user_info += "-"*40 + "\n"
            for user in user_info_data:
                user_info += f"{user['full_name']} | {user['age']} | {user['phone']} | @{user['username']}\n"
            await message.answer(user_info)
    else:
        await message.answer("У вас нет прав администратора для использования этой команды")



@dp.message(Mail.check_promo)
async def check_promo_code(message: Message, state: FSMContext):
    promo_code = message.text
    with open('promo_codes.txt', 'r') as file:
        promo_codes = file.read().splitlines()

    if promo_code in promo_codes:
        await message.answer(f"Промокод'{promo_code}' действительный")
    else:
        await message.answer(f"Промокод'{promo_code}' фигня собачья")

    await state.clear()


@dp.message()
async def handle_answer(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await cmd_start(message)
        return

    user_info = user_data[user_id]
    current_question = user_info["current_question"]

    if current_question < len(quiz_data):
        question_data = quiz_data[current_question]
        correct_answer = question_data["correct_answer"]
        additional_info = question_data["info"]

        if message.text == correct_answer:
            user_info["correct_answers"] += 1
            await message.reply("Совершенно верно!")
        else:
            await message.reply(f"Неа!")

        # Отправляем правильный ответ с дополнительной информацией и картинкой
        await bot.send_message(
            chat_id=message.chat.id,
            text= additional_info
        )

        user_info["current_question"] += 1
        await ask_question(message)
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Квиз завершен! Правильных ответов {user_info['correct_answers']} из {len(quiz_data)}",
            reply_markup=ReplyKeyboardRemove()  # убираем клавиатуру
        )
        # Clear user data
        user_data.pop(user_id)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())