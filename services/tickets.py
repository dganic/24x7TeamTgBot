import re
import asyncio
import ujson as json

from loguru import logger

from bot_loader import redis_client
from data.config import tickets_update_delay, ticket_tables, tickets_cache_time, inc_urn, sctask_urn
from libs.servicenow import ServiceNow

ticket_expiry = int(tickets_update_delay * 1.1)


async def get_tickets_data(snow_session: ServiceNow, tickets_urn: str, ticket_name: str):
    cache = await redis_client.get(f'cache_{ticket_name}')
    if cache:
        return json.loads(cache)
    else:
        tickets = snow_session.get_tickets(tickets_urn)['records']
        await redis_client.set(name=f'cache_{ticket_name}', value=json.dumps(tickets), ex=tickets_cache_time)
        return tickets


async def get_ticket_data(snow_session: ServiceNow, ticket_num: str):
    ticket_data = await redis_client.get(ticket_num)
    if ticket_data:
        logger.info(f'Ticket {ticket_num} found in database')
        return json.loads(ticket_data)
    else:
        ticket_type = re.findall('^[A-Za-z]+', ticket_num)[0].lower()
        ticket_urn = globals()[ticket_type + '_urn']
        logger.info(f'Ticket {ticket_num} not found in database')
        ticket_data = snow_session.get_tickets(ticket_urn + ticket_num)['records'][0]
        await save_ticket_data(ticket_num, ticket_data)
        return ticket_data


async def auto_update_tickets(snow_session: ServiceNow):
    while True:
        for ticket_table in ticket_tables:
            tickets = await get_tickets_data(snow_session,
                                             ticket_table['urn'],
                                             ticket_table['ticket_name']
                                             )
            if tickets:
                for ticket in tickets:
                    ticket_number = ticket['number']
                    if not await redis_client.get(ticket_number):
                        await redis_client.lpush('new_tickets', ticket_number)
                        logger.info(f'A new ticket {ticket_number} has been added to new_tickets queue')
                    await save_ticket_data(ticket_number, ticket)
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


async def save_ticket_data(ticket_number: str, ticket_data: dict):
    await redis_client.set(name=ticket_number, value=json.dumps(ticket_data), ex=ticket_expiry)
    logger.info(f'The ticket {ticket_number} has been added/updated to database')
