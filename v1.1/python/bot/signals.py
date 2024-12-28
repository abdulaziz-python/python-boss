from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from .views import set_webhook, run_async

@receiver(post_migrate)
def init_bot(sender, **kwargs):
    if settings.BOT_TOKEN:
        try:
            future = run_async(set_webhook())
            future.result() 
            print("Bot has been initialized and webhook set.")
        except Exception as e:
            print(f"Error initializing bot: {e}")
    else:
        print("BOT_TOKEN not found in settings. Bot initialization skipped.")

