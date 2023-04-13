
import requests
import json
import os
from dotenv import load_dotenv
from modules.api import Api
load_dotenv()

SEC_API_KEY = os.environ.get('SEC_API_KEY')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
SETTINGS_PATH = os.getenv('SETTINGS_PATH')
DATABASE_PATH = os.getenv('DATABASE_PATH')

api = Api(SEC_API_KEY)



        