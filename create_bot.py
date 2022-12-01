from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os, json

from aiogram.contrib.fsm_storage.memory import MemoryStorage

option_bot_path = os.getcwd() + "/" + "json/option_for_bot/option.json"
storage = MemoryStorage()
with open(option_bot_path, 'r', encoding='cp1251') as file:
    option_bot = json.load(file)
api_bot = option_bot["api_bot"]
bot = Bot(token=api_bot)
dp = Dispatcher(bot, storage=storage)
