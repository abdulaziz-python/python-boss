

TOKEN = '8087895131:AAGs2PUj9qZdL9U2mdvFCdM00ZNeSvFNaHc'
CHANNEL_ID = 'blazer_news'

import logging
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram import F

logging.basicConfig(level=logging.INFO)


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()

@dp.message(F.text == '/start')
async def start(message: Message):
    await message.reply("Salom! So'rovnomada qatnashish uchun kanalga a'zo bo'lishingiz kerak. Kanalga qo'shiling va keyin so'rovnomani boshlang!")

@dp.message()
async def check_membership(message: Message):
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if member.status in ['member', 'administrator', 'creator']:
        await survey(message)
    else:
        await message.reply("Iltimos, avval kanalga a'zo bo'ling!")

async def survey(message: Message):
    await message.reply("Boshqa savol yo'q, chunki bu so'rovnoma. Iltimos, javob bering!")

async def main():
    dp.include_router(dp.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
