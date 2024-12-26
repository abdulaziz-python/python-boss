from aiogram import Router, types, Dispatcher
from aiogram.filters import Command, CommandStart
from sqlalchemy.orm import Session
from database import get_db
import models

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    db = next(get_db())
    user = db.query(models.User).filter(models.User.telegram_id == message.from_user.id).first()
    if not user:
        user = models.User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        db.add(user)
        db.commit()

    await message.reply(f"Welcome, {message.from_user.full_name}! Use /help to see available commands.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/ban - Ban a user (admin only)\n"
        "/unban - Unban a user (admin only)\n"
        "/mute - Mute a user for 2 hours (admin only)\n"
        "/unmute - Unmute a user (admin only)\n"
        "/info - Show bot information\n"
        "/stats - Show bot statistics (admin only)"
    )
    await message.reply(help_text)

@router.message(Command("info"))
async def cmd_info(message: types.Message):
    db = next(get_db())
    user_count = db.query(models.User).count()
    chat_count = db.query(models.Chat).count()

    info_text = (
        f"Bot Information:\n"
        f"Total Users: {user_count}\n"
        f"Total Chats: {chat_count}\n"
        f"Bot Version: 1.0.0"
    )
    await message.reply(info_text)

def register_handlers(dp: Dispatcher):
    dp.include_router(router)

