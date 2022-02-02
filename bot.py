import asyncio
import logging

from loguru import logger
from aiogram import executor

import handlers

from bot_loader import dp, make_snow_bat_session
from services.logging import InterceptHandler
from services.notify_admins import on_startup_notify, new_tickets_notify
from services.tickets import auto_update_tickets, save_new_tickets

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)


async def start_tickets_auto_update():
    snow_bat_session = make_snow_bat_session()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    await asyncio.gather(
        asyncio.create_task(auto_update_tickets(snow_bat_session)),
        asyncio.create_task(save_new_tickets()),
        asyncio.create_task(new_tickets_notify(dp)),
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    )


async def on_startup(dispatcher):
    asyncio.create_task(on_startup_notify(dispatcher))
    asyncio.create_task(auto_update_tickets(snow_bat_session))
    asyncio.create_task(save_new_tickets())
    asyncio.create_task(new_tickets_notify(dispatcher))


if __name__ == '__main__':
    snow_bat_session = make_snow_bat_session()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
