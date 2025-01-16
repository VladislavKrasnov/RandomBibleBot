import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from data.config import TOKEN, BIBLE_PATH, USERS_DB, TOTAL_VERSES

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")

def add_user(user_id):
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        conn.commit()

def get_user_count():
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

bible_lines = []

async def load_bible_lines():
    global bible_lines
    try:
        with open(BIBLE_PATH, "r", encoding="utf-8") as file:
            bible_lines = file.readlines()
    except FileNotFoundError:
        bible_lines = []

def get_random_line():
    global bible_lines
    if not bible_lines:
        return None
    random_line = random.choice(bible_lines).strip()
    bible_lines.remove(random_line + "\n" if random_line + "\n" in bible_lines else random_line)
    
    with open(BIBLE_PATH, "w", encoding="utf-8") as file:
        file.writelines(bible_lines)
    return random_line

def get_remaining_verses():
    global bible_lines
    return len(bible_lines)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    add_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📦 Случайный стих"),
            types.KeyboardButton(text="📊 Статистика")]
        ],
        resize_keyboard=True
    )

    welcome_message = ("Добро пожаловать! Нажмите на кнопку, чтобы получить случайный стих.")
    await message.answer(welcome_message, parse_mode=ParseMode.HTML, reply_markup=markup)

@dp.message(lambda message: message.text == "📦 Случайный стих")
async def send_random_poem(message: Message):
    random_line = get_random_line()
    if random_line:
        await message.answer(random_line)
    else:
        await message.answer("Файл со стихами пуст или не найден.")

@dp.message(lambda message: message.text == "📊 Статистика")
async def send_statistics(message: Message):
    remaining_verses = get_remaining_verses()
    issued_verses = TOTAL_VERSES - remaining_verses
    user_count = get_user_count()

    stats_message = (
        f"📊 <b>Статистика</b>\n"
        f"Всего выдано стихов: {issued_verses}\n"
        f"Пользователей бота: {user_count}\n"
    )
    await message.answer(stats_message, parse_mode=ParseMode.HTML)
    

async def on_startup():
    await load_bible_lines()

if __name__ == "__main__":
    init_db()
    async def main():
        await on_startup()
        await dp.start_polling(bot)

    asyncio.run(main())