from aiogram import Router, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import sync_to_async
from bot.models import User, Chat, BannedUser, MutedUser, GroupAdmin, Rule
from django.conf import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

async def is_admin(user_id: int, chat_id: int):
    if user_id == settings.ADMIN_ID or user_id == 1087968824:
        return True

    group_admin = await sync_to_async(GroupAdmin.objects.filter)(
        chat__telegram_id=chat_id,
        user__telegram_id=user_id
    )
    return await sync_to_async(group_admin.exists)()


async def is_anonymous_admin(user: types.User, chat: types.Chat):
    if not user.is_anonymous:
        return False
    anonymous_id = f"{user.id}_{chat.id}"
    group_admin = await sync_to_async(GroupAdmin.objects.filter)(
        chat__telegram_id=chat.id,
        is_anonymous=True,
        anonymous_id=anonymous_id
    )
    return await sync_to_async(group_admin.exists)()

async def save_group_admin(user: types.User, chat: types.Chat):
    chat_obj, _ = await sync_to_async(Chat.objects.get_or_create)(
        telegram_id=chat.id,
        defaults={'title': chat.title}
    )
    if user.is_anonymous:
        anonymous_id = f"{user.id}_{chat.id}"
        await sync_to_async(GroupAdmin.objects.get_or_create)(
            chat=chat_obj,
            is_anonymous=True,
            anonymous_id=anonymous_id
        )
    else:
        user_obj, _ = await sync_to_async(User.objects.get_or_create)(
            telegram_id=user.id,
            defaults={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )
        await sync_to_async(GroupAdmin.objects.get_or_create)(
            user=user_obj,
            chat=chat_obj
        )

@router.message(Command("ban"))
async def ban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Iltimos, taqiqlamoqchi bo'lgan foydalanuvchining xabariga javob bering.")
        return

    if not await is_admin(message.from_user.id, message.chat.id) and not await is_anonymous_admin(message.from_user, message.chat):
        await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo'q.")
        return

    user_to_ban = message.reply_to_message.from_user
    chat, _ = await sync_to_async(Chat.objects.get_or_create)(
        telegram_id=message.chat.id,
        defaults={'title': message.chat.title}
    )

    user, _ = await sync_to_async(User.objects.get_or_create)(
        telegram_id=user_to_ban.id,
        defaults={
            'username': user_to_ban.username,
            'first_name': user_to_ban.first_name,
            'last_name': user_to_ban.last_name
        }
    )

    admin, _ = await sync_to_async(User.objects.get_or_create)(
        telegram_id=message.from_user.id,
        defaults={
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
    )

    await sync_to_async(BannedUser.objects.create)(user=user, chat=chat, banned_by=admin)

    await message.bot.ban_chat_member(chat_id=message.chat.id, user_id=user_to_ban.id)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Nima uchun?", callback_data=f"why_banned_{user_to_ban.id}")]
    ])
    
    ban_message = (
        f"*Foydalanuvchi taqiqlandi* ⛔️\n\n"
        f"👤 Foydalanuvchi: [{user_to_ban.full_name}](tg://user?id={user_to_ban.id})\n"
        f"🆔 ID: `{user_to_ban.id}`\n"
        f"👮 Admin: [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n"
        f"📅 Sana: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.reply(ban_message, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("unban"))
async def unban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Iltimos, taqiqdan chiqarmoqchi bo'lgan foydalanuvchining xabariga javob bering.")
        return

    if not await is_admin(message.from_user.id, message.chat.id) and not await is_anonymous_admin(message.from_user, message.chat):
        await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo'q.")
        return

    user_to_unban = message.reply_to_message.from_user
    chat = await sync_to_async(Chat.objects.get)(telegram_id=message.chat.id)
    user = await sync_to_async(User.objects.get)(telegram_id=user_to_unban.id)

    @sync_to_async
    def get_banned_user():
        return BannedUser.objects.filter(user=user, chat=chat).first()

    @sync_to_async
    def delete_banned_user(banned_user):
        banned_user.delete()

    banned_user = await get_banned_user()
    if banned_user:
        await delete_banned_user(banned_user)

    await message.bot.unban_chat_member(chat_id=message.chat.id, user_id=user_to_unban.id)
    
    unban_message = (
        f"*Foydalanuvchi taqiqdan chiqarildi* ✅\n\n"
        f"👤 Foydalanuvchi: [{user_to_unban.full_name}](tg://user?id={user_to_unban.id})\n"
        f"🆔 ID: `{user_to_unban.id}`\n"
        f"👮 Admin: [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n"
        f"📅 Sana: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.reply(unban_message, parse_mode='Markdown')

@router.message(Command("mute"))
async def mute_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Iltimos, ovozini o'chirmoqchi bo'lgan foydalanuvchining xabariga javob bering.")
        return

    if not await is_admin(message.from_user.id, message.chat.id) and not await is_anonymous_admin(message.from_user, message.chat):
        await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo'q.")
        return

    user_to_mute = message.reply_to_message.from_user
    chat, _ = await sync_to_async(Chat.objects.get_or_create)(
        telegram_id=message.chat.id,
        defaults={'title': message.chat.title}
    )

    user, _ = await sync_to_async(User.objects.get_or_create)(
        telegram_id=user_to_mute.id,
        defaults={
            'username': user_to_mute.username,
            'first_name': user_to_mute.first_name,
            'last_name': user_to_mute.last_name
        }
    )

    admin, _ = await sync_to_async(User.objects.get_or_create)(
        telegram_id=message.from_user.id,
        defaults={
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
    )

    mute_until = timezone.now() + timedelta(seconds=settings.MUTE_DURATION)
    await sync_to_async(MutedUser.objects.create)(user=user, chat=chat, muted_until=mute_until, muted_by=admin)

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_to_mute.id,
        permissions=types.ChatPermissions(can_send_messages=False),
        until_date=mute_until
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Nima uchun?", callback_data=f"why_muted_{user_to_mute.id}")]
    ])
    
    mute_message = (
        f"*Foydalanuvchi ovozi o'chirildi* 🔇\n\n"
        f"👤 Foydalanuvchi: [{user_to_mute.full_name}](tg://user?id={user_to_mute.id})\n"
        f"🆔 ID: `{user_to_mute.id}`\n"
        f"👮 Admin: [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n"
        f"⏱ Muddat: 2 soat\n"
        f"📅 Sana: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.reply(mute_message, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("unmute"))
async def unmute_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Iltimos, ovozini yoqmoqchi bo'lgan foydalanuvchining xabariga javob bering.")
        return

    if not await is_admin(message.from_user.id, message.chat.id) and not await is_anonymous_admin(message.from_user, message.chat):
        await message.reply("Sizda bu buyruqni ishlatish uchun ruxsat yo'q.")
        return

    user_to_unmute = message.reply_to_message.from_user
    chat = await sync_to_async(Chat.objects.get)(telegram_id=message.chat.id)
    user = await sync_to_async(User.objects.get)(telegram_id=user_to_unmute.id)

    @sync_to_async
    def get_muted_user():
        return MutedUser.objects.filter(user=user, chat=chat).first()

    @sync_to_async
    def delete_muted_user(muted_user):
        muted_user.delete()

    muted_user = await get_muted_user()
    if muted_user:
        await delete_muted_user(muted_user)

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_to_unmute.id,
        permissions=types.ChatPermissions(can_send_messages=True)
    )
    
    unmute_message = (
        f"*Foydalanuvchi ovozi yoqildi* 🔊\n\n"
        f"👤 Foydalanuvchi: [{user_to_unmute.full_name}](tg://user?id={user_to_unmute.id})\n"
        f"🆔 ID: `{user_to_unmute.id}`\n"
        f"👮 Admin: [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n"
        f"📅 Sana: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.reply(unmute_message, parse_mode='Markdown')

@router.message(Command("admins"))
async def list_admins(message: types.Message):
    chat = await sync_to_async(Chat.objects.get)(telegram_id=message.chat.id)
    admins = await sync_to_async(list)(GroupAdmin.objects.filter(chat=chat))
    
    admin_list = "*Guruh adminlari:*\n\n"
    for admin in admins:
        if admin.is_anonymous:
            admin_list += "👤 Anonim Admin\n"
        else:
            admin_list += f"👤 [{admin.user.first_name} {admin.user.last_name or ''}](tg://user?id={admin.user.telegram_id}) (@{admin.user.username or 'N/A'})\n"
    
    await message.reply(admin_list, parse_mode='Markdown')

@router.message(Command("rules"))
async def show_rules(message: types.Message):
    rules = await sync_to_async(list)(Rule.objects.all())
    
    if not rules:
        await message.reply("Bu guruh uchun hech qanday qoida o'rnatilmagan.")
        return
    
    rules_text = "*Guruh qoidalari:*\n\n"
    for rule in rules:
        rules_text += f"• {rule.title}\n"
    
    rules_text += "\nBatafsil ma'lumot uchun quyidagi tugmani bosing."
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Qoidalarni to'liq o'qish", url="https://t.me/python_ruless")]
    ])
    
    await message.reply(rules_text, reply_markup=keyboard, parse_mode='Markdown')

@router.callback_query(F.data.startswith("why_banned_"))
async def why_banned(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    await callback_query.answer("Siz guruh qoidalarini buzganingiz uchun taqiqlandingiz. Qoidalar haqida ko'proq ma'lumot: https://t.me/python_ruless", show_alert=True)

@router.callback_query(F.data.startswith("why_muted_"))
async def why_muted(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    await callback_query.answer("Siz guruh qoidalarini buzganingiz uchun ovozingiz o'chirildi. Qoidalar haqida ko'proq ma'lumot: https://t.me/python_ruless", show_alert=True)

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: types.ChatMemberUpdated):
    new_member = event.new_chat_member.user
    welcome_message = (
        f"Assalomu alaykum, [{new_member.full_name}](tg://user?id={new_member.id})! 👋\n\n"
        f"Guruhimizga xush kelibsiz. Iltimos, guruh qoidalari bilan tanishib chiqing va ularga rioya qiling."
    )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Guruh qoidalari", url="https://t.me/python_ruless")]
    ])
    
    sent_message = await event.bot.send_message(event.chat.id, welcome_message, reply_markup=keyboard, parse_mode='Markdown')
    \
    await event.bot.delete_message(event.chat.id, event.action_message.message_id)
    
    await asyncio.sleep(300)    
    await event.bot.delete_message(event.chat.id, sent_message.message_id)

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: types.ChatMemberUpdated):
    await event.bot.delete_message(event.chat.id, event.action_message.message_id)

@router.message(F.new_chat_members)
async def on_new_chat_members(message: types.Message):
    await message.delete()

@router.message(F.left_chat_member)
async def on_left_chat_member(message: types.Message):
    await message.delete()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_MEMBER))
async def on_admin_status_change(event: types.ChatMemberUpdated):
    if event.new_chat_member.status in ['creator', 'administrator']:
        await save_group_admin(event.new_chat_member.user, event.chat)
        logger.info(f"Yangi admin saqlandi: {event.new_chat_member.user.full_name} guruhda {event.chat.title}")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_MEMBER))
async def on_admin_status_change(event: types.ChatMemberUpdated):
    if event.new_chat_member.status in ['creator', 'administrator']:
        await save_group_admin(event.new_chat_member.user, event.chat)
        logger.info(f"Yangi admin saqlandi: {event.new_chat_member.user.full_name} guruhda {event.chat.title}")

