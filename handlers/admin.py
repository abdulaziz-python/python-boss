from aiogram import Router, types, Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm import Session
from database import get_db
import models
from config import ADMIN_ID

router = Router()

@router.message(Command("stats"))
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("You don't have permission to use this command.")
        return

    db = next(get_db())
    user_count = db.query(models.User).count()
    chat_count = db.query(models.Chat).count()
    banned_count = db.query(models.BannedUser).count()
    muted_count = db.query(models.MutedUser).count()

    stats = f"Bot Statistics:\n\n" \
            f"Users: {user_count}\n" \
            f"Chats: {chat_count}\n" \
            f"Banned Users: {banned_count}\n" \
            f"Muted Users: {muted_count}"

    await message.reply(stats)

def register_handlers(dp: Dispatcher):
    dp.include_router(router)

