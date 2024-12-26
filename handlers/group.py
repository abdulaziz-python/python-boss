from aiogram import Router, types, Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm import Session
from database import get_db
import models
from datetime import datetime, timedelta
from config import MUTE_DURATION

router = Router()

@router.message(Command("ban"))
async def ban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a user's message to ban them.")
        return

    db = next(get_db())
    admin = db.query(models.User).filter(models.User.telegram_id == message.from_user.id).first()
    if not admin or not admin.is_admin:
        await message.reply("You don't have permission to use this command.")
        return

    user_to_ban = message.reply_to_message.from_user
    chat = db.query(models.Chat).filter(models.Chat.telegram_id == message.chat.id).first()
    if not chat:
        chat = models.Chat(telegram_id=message.chat.id, title=message.chat.title)
        db.add(chat)
        db.commit()

    user = db.query(models.User).filter(models.User.telegram_id == user_to_ban.id).first()
    if not user:
        user = models.User(telegram_id=user_to_ban.id, username=user_to_ban.username,
                           first_name=user_to_ban.first_name, last_name=user_to_ban.last_name)
        db.add(user)
        db.commit()

    banned_user = models.BannedUser(user_id=user.id, chat_id=chat.id)
    db.add(banned_user)
    db.commit()

    await message.bot.ban_chat_member(chat_id=message.chat.id, user_id=user_to_ban.id)
    await message.reply(f"User {user_to_ban.full_name} has been banned.")

@router.message(Command("unban"))
async def unban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a user's message to unban them.")
        return

    db = next(get_db())
    admin = db.query(models.User).filter(models.User.telegram_id == message.from_user.id).first()
    if not admin or not admin.is_admin:
        await message.reply("You don't have permission to use this command.")
        return

    user_to_unban = message.reply_to_message.from_user
    chat = db.query(models.Chat).filter(models.Chat.telegram_id == message.chat.id).first()
    user = db.query(models.User).filter(models.User.telegram_id == user_to_unban.id).first()

    if chat and user:
        banned_user = db.query(models.BannedUser).filter(
            models.BannedUser.user_id == user.id,
            models.BannedUser.chat_id == chat.id
        ).first()
        if banned_user:
            db.delete(banned_user)
            db.commit()

    await message.bot.unban_chat_member(chat_id=message.chat.id, user_id=user_to_unban.id)
    await message.reply(f"User {user_to_unban.full_name} has been unbanned.")

@router.message(Command("mute"))
async def mute_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a user's message to mute them.")
        return

    db = next(get_db())
    admin = db.query(models.User).filter(models.User.telegram_id == message.from_user.id).first()
    if not admin or not admin.is_admin:
        await message.reply("You don't have permission to use this command.")
        return

    user_to_mute = message.reply_to_message.from_user
    chat = db.query(models.Chat).filter(models.Chat.telegram_id == message.chat.id).first()
    if not chat:
        chat = models.Chat(telegram_id=message.chat.id, title=message.chat.title)
        db.add(chat)
        db.commit()

    user = db.query(models.User).filter(models.User.telegram_id == user_to_mute.id).first()
    if not user:
        user = models.User(telegram_id=user_to_mute.id, username=user_to_mute.username,
                           first_name=user_to_mute.first_name, last_name=user_to_mute.last_name)
        db.add(user)
        db.commit()

    mute_until = datetime.utcnow() + timedelta(seconds=MUTE_DURATION)
    muted_user = models.MutedUser(user_id=user.id, chat_id=chat.id, muted_until=mute_until)
    db.add(muted_user)
    db.commit()

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_to_mute.id,
        permissions=types.ChatPermissions(can_send_messages=False),
        until_date=mute_until
    )
    await message.reply(f"User {user_to_mute.full_name} has been muted for 2 hours.")

@router.message(Command("unmute"))
async def unmute_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Please reply to a user's message to unmute them.")
        return

    db = next(get_db())
    admin = db.query(models.User).filter(models.User.telegram_id == message.from_user.id).first()
    if not admin or not admin.is_admin:
        await message.reply("You don't have permission to use this command.")
        return

    user_to_unmute = message.reply_to_message.from_user
    chat = db.query(models.Chat).filter(models.Chat.telegram_id == message.chat.id).first()
    user = db.query(models.User).filter(models.User.telegram_id == user_to_unmute.id).first()

    if chat and user:
        muted_user = db.query(models.MutedUser).filter(
            models.MutedUser.user_id == user.id,
            models.MutedUser.chat_id == chat.id
        ).first()
        if muted_user:
            db.delete(muted_user)
            db.commit()

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_to_unmute.id,
        permissions=types.ChatPermissions(can_send_messages=True)
    )
    await message.reply(f"User {user_to_unmute.full_name} has been unmuted.")

def register_handlers(dp: Dispatcher):
    dp.include_router(router)

