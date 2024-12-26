import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import admin, group, user
from database import engine
import models

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    admin.register_handlers(dp)
    group.register_handlers(dp)
    user.register_handlers(dp)

    await bot.set_my_commands([
        types.BotCommand(command="/start", description="Start the bot"),
        types.BotCommand(command="/help", description="Show help message"),
        types.BotCommand(command="/ban", description="Ban a user"),
        types.BotCommand(command="/unban", description="Unban a user"),
        types.BotCommand(command="/mute", description="Mute a user for 2 hours"),
        types.BotCommand(command="/unmute", description="Unmute a user"),
        types.BotCommand(command="/info", description="Bot info"),
        types.BotCommand(command="/stats", description="Show bot statistics"),
    ])

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

