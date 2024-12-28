from aiogram import Router, types, Dispatcher
from aiogram.types import CallbackQuery
from config import banned_users, muted_users, MUTE_DURATION
from utils import escape_markdown
import time

router = Router()

@router.callback_query(lambda c: c.data.startswith(('ban_', 'unban_', 'mute_', 'unmute_', 'info_')))
async def process_callback(callback_query: CallbackQuery):
    action, user_id = callback_query.data.split('_')
    user_id = int(user_id)
    chat_id = callback_query.message.chat.id
    
    if action == 'ban':
        await callback_query.bot.ban_chat_member(chat_id, user_id)
        if chat_id not in banned_users:
            banned_users[chat_id] = []
        banned_users[chat_id].append(user_id)
        await callback_query.answer("User banned successfully.")
        await callback_query.message.edit_text(
            f"🚫 User `{user_id}` has been banned from the group.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="✅ Unban User", callback_data=f"unban_{user_id}")]
            ])
        )
    
    elif action == 'unban':
        await callback_query.bot.unban_chat_member(chat_id, user_id)
        if chat_id in banned_users and user_id in banned_users[chat_id]:
            banned_users[chat_id].remove(user_id)
        await callback_query.answer("User unbanned successfully.")
        await callback_query.message.edit_text(
            f"✅ User `{user_id}` has been unbanned from the group.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🚫 Ban User", callback_data=f"ban_{user_id}")]
            ])
        )
    
    elif action == 'mute':
        await callback_query.bot.restrict_chat_member(
            chat_id, user_id,
            types.ChatPermissions(can_send_messages=False),
            until_date=time.time() + MUTE_DURATION.total_seconds()
        )
        muted_users[chat_id] = muted_users.get(chat_id, {})
        muted_users[chat_id][user_id] = time.time() + MUTE_DURATION.total_seconds()
        await callback_query.answer("User muted successfully.")
        await callback_query.message.edit_text(
            f"🔇 User `{user_id}` has been muted for 2 hours.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🔊 Unmute User", callback_data=f"unmute_{user_id}")]
            ])
        )
    
    elif action == 'unmute':
        await callback_query.bot.restrict_chat_member(
            chat_id, user_id,
            types.ChatPermissions(can_send_messages=True)
        )
        if chat_id in muted_users and user_id in muted_users[chat_id]:
            del muted_users[chat_id][user_id]
        await callback_query.answer("User unmuted successfully.")
        await callback_query.message.edit_text(
            f"🔊 User `{user_id}` has been unmuted.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🔇 Mute User", callback_data=f"mute_{user_id}")]
            ])
        )
    
    elif action == 'info':
        user = await callback_query.bot.get_chat_member(chat_id, user_id)
        user_info = (
            f"*User Information:*\n"
            f"• Name: {escape_markdown(user.user.full_name)}\n"
            f"• Username: @{user.user.username}\n"
            f"• User ID: `{user.user.id}`\n"
            f"• Is Admin: {'Yes' if user.is_chat_admin() else 'No'}\n"
            f"• Joined: {user.joined_date.strftime('%Y-%m-%d %H:%M:%S') if user.joined_date else 'Unknown'}"
        )
        await callback_query.answer()
        await callback_query.message.edit_text(
            user_info,
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="🚫 Ban", callback_data=f"ban_{user_id}"),
                    types.InlineKeyboardButton(text="🔇 Mute", callback_data=f"mute_{user_id}")
                ]
            ])
        )

def register_callback_handlers(dp: Dispatcher):
    dp.include_router(router)

