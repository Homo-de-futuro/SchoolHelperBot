from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv, find_dotenv
import os

#variables and const
load_dotenv(find_dotenv())

#create bot
bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

scheduler = AsyncIOScheduler()



