from django.apps import AppConfig
import os

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        
        from .views import on_startup, run_async
        future = run_async(on_startup())
        future.result()  

