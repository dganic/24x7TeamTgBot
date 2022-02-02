import asyncio
import ujson as json

from loguru import logger
from aiogram import Dispatcher

from bot_loader import redis_client
from data.config import admin_ids, tickets_notify_delay
from services.messages import create_ticket_msg


async def on_startup_notify(dp: Dispatcher):
    for admin_id in admin_ids:
        try:
            await dp.bot.send_message(admin_id, "24х7 Team Bot has been started")
            logger.info(f'Startup message send to {admin_id}')

        except Exception as err:
            logger.exception(err)


async def new_tickets_notify(dp: Dispatcher):
    while True:
        subscriber_ids = await redis_client.lrange('subscriber_ids', 0, -1)
        logger.info(f'Subscriber ids: {subscriber_ids}')
        for id in subscriber_ids:
            new_tickets = await redis_client.lrange(f'new_tickets_{id}', 0, -1)
            logger.info(f'A new tickets {new_tickets} for id: {id}')
            if new_tickets:
                await dp.bot.send_message(chat_id=id, text='<b>New ticket in the stack</b>')
            for new_ticket in new_tickets:
                ticket_data = json.loads(await redis_client.get(new_ticket))
                msg = await create_ticket_msg(ticket_data, accepted=False)
                await dp.bot.send_message(chat_id=id, text=msg.msg, reply_markup=msg.keyboard)
        await asyncio.sleep(tickets_notify_delay)

