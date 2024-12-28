import logging
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from asgiref.sync import async_to_sync
from .handlers import admin, group, user
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

session = AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(admin.router)
dp.include_router(group.router)
dp.include_router(user.router)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_async(coroutine):
    return asyncio.run_coroutine_threadsafe(coroutine, loop)

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        try:
            logger.debug(f"Received webhook request: {request.body.decode('utf-8')}")
            update_data = json.loads(request.body)
            update = Update(**update_data)
            
            async def process_update():
                try:
                    await dp.feed_update(bot=bot, update=update)
                    logger.debug("Update processed successfully")
                except Exception as e:
                    logger.error(f"Error in process_update: {e}", exc_info=True)

            future = run_async(process_update())
            future.result()
            return HttpResponse("OK")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook request: {e}", exc_info=True)
            return HttpResponse("Invalid JSON", status=400)
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            return HttpResponse(f"Error: {str(e)}", status=400)
    return HttpResponse("Method not allowed", status=405)

def index(request):
    return render(request, 'bot/index.html')

async def set_webhook():
    try:
        await bot.delete_webhook()
        webhook_info = await bot.set_webhook(url=settings.WEBHOOK_URL)
        logger.info(f"Webhook set to {settings.WEBHOOK_URL}")
        logger.info(f"Webhook info: {webhook_info}")

        await bot.set_my_commands([
            types.BotCommand(command="/start", description="Start the bot"),
            types.BotCommand(command="/help", description="Show help message"),
            types.BotCommand(command="/ban", description="Ban a user"),
            types.BotCommand(command="/unban", description="Unban a user"),
            types.BotCommand(command="/mute", description="Mute a user for 2 hours"),
            types.BotCommand(command="/unmute", description="Unmute a user"),
            types.BotCommand(command="/info", description="Bot info"),
            types.BotCommand(command="/stats", description="Show bot statistics"),
            types.BotCommand(command="/rules", description="Show group rules"),
        ])
        logger.info("Bot commands set")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}", exc_info=True)
        raise

async def on_startup():
    await set_webhook()
    logger.info("Bot started")

async def on_shutdown():
    await bot.session.close()
    logger.info("Bot stopped")

def run_event_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

import threading
threading.Thread(target=run_event_loop, daemon=True).start()

