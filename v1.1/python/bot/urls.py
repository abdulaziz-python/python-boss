from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path(f'webhook/{settings.BOT_TOKEN}', views.webhook, name='webhook'), 
]

