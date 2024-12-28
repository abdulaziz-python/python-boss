from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User, Chat, GroupAdmin, BannedUser, MutedUser, Rule, BroadcastMessage
from aiogram import Bot, types
from django.conf import settings
import asyncio
import json
from asgiref.sync import sync_to_async

bot = Bot(token=settings.BOT_TOKEN)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'last_name', 'is_admin', 'created_at')
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    list_filter = ('is_admin', 'created_at')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'title', 'created_at')
    search_fields = ('telegram_id', 'title')
    list_filter = ('created_at',)

@admin.register(GroupAdmin)
class GroupAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'is_anonymous', 'created_at')
    list_filter = ('is_anonymous', 'created_at')
    search_fields = ('user__username', 'chat__title')

@admin.register(BannedUser)
class BannedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'banned_at', 'banned_by')
    list_filter = ('banned_at',)
    search_fields = ('user__username', 'chat__title')

@admin.register(MutedUser)
class MutedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'muted_at', 'muted_until', 'muted_by')
    list_filter = ('muted_at', 'muted_until')
    search_fields = ('user__username', 'chat__title')

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')

@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    change_list_template = 'admin/broadcast_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('broadcast/', self.broadcast_message, name='broadcast_message'),
        ]
        return custom_urls + urls

    def broadcast_message(self, request):
        if request.method == 'POST':
            message = request.POST.get('message')
            image_url = request.POST.get('image_url')
            keyboard = request.POST.get('keyboard')

            try:
                keyboard_json = json.loads(keyboard) if keyboard else None
            except json.JSONDecodeError:
                self.message_user(request, "Invalid JSON format for inline keyboard", level='ERROR')
                return HttpResponseRedirect(reverse('admin:index'))

            BroadcastMessage.objects.create(
                message=message,
                image_url=image_url,
                keyboard=keyboard
            )

            async def send_broadcast():
                users = await sync_to_async(list)(User.objects.all())
                chats = await sync_to_async(list)(Chat.objects.all())

                for user in users:
                    try:
                        if image_url:
                            await bot.send_photo(user.telegram_id, image_url, caption=message, reply_markup=keyboard_json, parse_mode='MarkdownV2')
                        else:
                            await bot.send_message(user.telegram_id, message, reply_markup=keyboard_json, parse_mode='MarkdownV2')
                    except Exception as e:
                        print(f"Error sending message to user {user.telegram_id}: {e}")

                for chat in chats:
                    try:
                        if image_url:
                            await bot.send_photo(chat.telegram_id, image_url, caption=message, reply_markup=keyboard_json, parse_mode='MarkdownV2')
                        else:
                            await bot.send_message(chat.telegram_id, message, reply_markup=keyboard_json, parse_mode='MarkdownV2')
                    except Exception as e:
                        print(f"Error sending message to chat {chat.telegram_id}: {e}")

            asyncio.run(send_broadcast())
            self.message_user(request, "Broadcast sent successfully")
            return HttpResponseRedirect(reverse('admin:index'))
        return render(request, 'admin/broadcast_form.html')

