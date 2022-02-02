import aioredis

from loguru import logger
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from libs import ServiceNow

snow_bat_session: ServiceNow

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

redis_client = aioredis.from_url(
    url=config.redis_url,
    password=config.redis_password,
    encoding="utf-8",
    decode_responses=True
)


def make_snow_bat_session():
    global snow_bat_session
    snow_bat_session = ServiceNow(config.inst_url_bat)
    return snow_bat_session
