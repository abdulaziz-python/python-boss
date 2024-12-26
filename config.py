import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', "6846608037:AAEQYLvOXyxSTj3bwAk5cZywfs9WebDkzbo")
ADMIN_ID = int(os.getenv('ADMIN_ID'))
DATABASE_URL = os.getenv('DATABASE_URL')

MUTE_DURATION = 7200  # 2 soatga mute oladi

