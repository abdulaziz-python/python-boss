import logging
from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from asgiref.sync import sync_to_async
from bot.models import User

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        user, created = await sync_to_async(User.objects.get_or_create)(
            telegram_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )
        
        welcome_text = f"Assalomu Alaykum, {message.from_user.full_name}! Python Boss botiga hush kelibsiz.\nBu bot sizni guruhingizni boshqarishda yordam beradi. Shunchaki botni guruhga qo'shing.\nKo'proq ma'lumot olish uchun /help kamandasidan foydalaning"
        
        try:
            await message.reply(welcome_text)
        except Exception as e:
            logger.error(f"Failed to reply to message: {e}")
            await message.answer(welcome_text)
        
        logger.info(f"Start command processed for user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Available commands:\n"
        "/start - Botni ishga tushirish\n"
        "/help -Bot haqida to'liq ma'lumot\n"
        "/ban - foydalanuvchini ban qilish (admin)\n"
        "/unban - bandan chiqarish (admin)\n"
        "/mute - foydalanuvchini 2 soatga mute qilish (admin)\n"
        "/unmute - mutedan chiqarish (admin)\n"
        "/info - Bot haqidagi ma'lumotlar\n"
        "/stats - Statistika (admin)"
    )
    await message.reply(help_text)

@router.message(Command("info"))
async def cmd_info(message: types.Message):
    user_count = await sync_to_async(User.objects.count)()
    
    info_text = (
        f"Bot Malumoti:\n"
        f"Jami foydalanuvchi: {user_count}\n"
        f"Bot Version: 1.0.0"
    )
    await message.reply(info_text)

