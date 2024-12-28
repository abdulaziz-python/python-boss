from aiogram import Router, types, F
from aiogram.filters import Command
from django.conf import settings
from asgiref.sync import sync_to_async
from bot.models import User, Chat, BannedUser, MutedUser

router = Router()

@router.message(Command("stats"))
async def show_stats(message: types.Message):
    if message.from_user.id != settings.ADMIN_ID:
        await message.reply("You don't have permission to use this command.")
        return

    user_count = await sync_to_async(User.objects.count)()
    chat_count = await sync_to_async(Chat.objects.count)()
    banned_count = await sync_to_async(BannedUser.objects.count)()
    muted_count = await sync_to_async(MutedUser.objects.count)()

    stats = f"Bot Statistics:\n\n" \
            f"Users: {user_count}\n" \
            f"Chats: {chat_count}\n" \
            f"Banned Users: {banned_count}\n" \
            f"Muted Users: {muted_count}"

    await message.reply(stats)

