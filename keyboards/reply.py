from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add to Group", url="http://t.me/chat_blazer_bot?startgroup=start")],
            [InlineKeyboardButton(text="📢 Join Updates Channel", url="https://t.me/blazer_news")]
        ]
    )

def get_admin_keyboard(user_id: int, action: str):
    if action == "ban":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚫 Ban User", callback_data=f"ban_{user_id}")]
            ]
        )
    elif action == "unban":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Unban User", callback_data=f"unban_{user_id}")]
            ]
        )
    elif action == "mute":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔇 Mute User", callback_data=f"mute_{user_id}")]
            ]
        )
    elif action == "unmute":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔊 Unmute User", callback_data=f"unmute_{user_id}")]
            ]
        )
    )

def get_user_info_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚫 Ban", callback_data=f"ban_{user_id}"),
                InlineKeyboardButton(text="🔇 Mute", callback_data=f"mute_{user_id}")
            ],
            [InlineKeyboardButton(text="ℹ️ User Info", callback_data=f"info_{user_id}")]
        ]
    )

