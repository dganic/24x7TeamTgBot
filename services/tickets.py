import asyncio
import ujson as json

from loguru import logger

from bot_loader import redis_client
from data.config import tickets_update_delay, ticket_tables, tickets_cache_time
from libs.servicenow import ServiceNow


async def get_tickets_data(snow_session: ServiceNow, ticket_url: str, ticket_name: str):
    cache = await redis_client.get(f'cache_{ticket_name}')
    if cache:
        return json.loads(cache)
    else:
        tickets = snow_session.get_tickets(ticket_url)['records']
        await redis_client.set(name=f'cache_{ticket_name}', value=json.dumps(tickets), ex=tickets_cache_time)
        return tickets


async def auto_update_tickets(snow_session: ServiceNow):
    ticket_expiry = int(tickets_update_delay * 1.1)
    while True:
        for ticket_table in ticket_tables:
            tickets = await get_tickets_data(snow_session,
                                             ticket_table['url'],
                                             ticket_table['ticket_name']
                                             )
            if tickets:
                for ticket in tickets:
                    ticket_number = ticket['number']

                    if not await redis_client.get(ticket_number):
                        await redis_client.lpush('new_tickets', ticket_number)
                        logger.info(f'A new ticket {ticket_number} has been added to new_tickets queue')
                    await redis_client.set(name=ticket['number'], value=json.dumps(ticket), ex=ticket_expiry)
                    logger.info(f'The ticket {ticket_number} has been added/updated to database')
        logger.info(f'Wait {tickets_update_delay} seconds before the next ticket update')
        await asyncio.sleep(tickets_update_delay)


async def save_new_tickets():
    while True:
        new_ticket = (await redis_client.brpop('new_tickets'))[1]
        logger.info(f'A new ticket {new_ticket} has been received from the new_tickets queue')
        subscriber_ids = await redis_client.lrange('subscriber_ids', 0, -1)
        for tg_id in subscriber_ids:
            await redis_client.rpush(f'new_tickets_{tg_id}', str(new_ticket))
            logger.info(f'A new ticket {new_ticket} has been added to new_tickets_{tg_id} list')

