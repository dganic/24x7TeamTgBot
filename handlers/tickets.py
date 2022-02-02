from loguru import logger
from aiogram import types
from aiogram.dispatcher.filters import IDFilter, Text

import bot_loader

from bot_loader import dp
from data.config import duty_team_ids, incidents_urn_bat, tasks_urn_bat
from keyboards.kb_tickets import cb_ticket_data
from services.messages import edit_ticket_msg, create_ticket_msg, AnswerMessages
from services.tickets import get_tickets_data, get_ticket_data, save_ticket_data


@dp.message_handler(IDFilter(user_id=duty_team_ids), Text(startswith='get', ignore_case=True))
async def get_tickets_bat(message: types.Message):
    ticket_name = message.text.split(' ')[1]
    logger.debug(f'Ticket name: {ticket_name}')
    if ticket_name == 'incidents':
        incidents = await get_tickets_data(bot_loader.snow_bat_session, incidents_urn_bat, ticket_name)
        for incident in incidents:
            await save_ticket_data(incident['number'], incident)
            msg = await create_ticket_msg(incident)
            await message.answer(text=msg.msg, reply_markup=msg.keyboard)
    elif ticket_name == 'tasks':
        tasks = await get_tickets_data(bot_loader.snow_bat_session, tasks_urn_bat, ticket_name)
        for task in tasks:
            await save_ticket_data(task['number'], task)
            msg = await create_ticket_msg(task)
            await message.answer(text=msg.msg, reply_markup=msg.keyboard)


@dp.callback_query_handler(cb_ticket_data.filter())
async def ticket_callback(call: types.CallbackQuery, callback_data: dict):
    ticket_num = callback_data['ticket_number']
    field = callback_data['action']
    ticket_data = await get_ticket_data(bot_loader.snow_bat_session, ticket_num)
    if field == 'ticket':
        new_tickets = await bot_loader.redis_client.lrange(f'new_tickets_{call.from_user.id}', 0, -1)
        if ticket_num in new_tickets:
            msg = await create_ticket_msg(ticket_data, accepted=False)
        else:
            msg = await create_ticket_msg(ticket_data)
        await call.message.edit_text(text=msg.msg, reply_markup=msg.keyboard)
        await call.answer()
    elif field == 'accepted':
        await bot_loader.redis_client.lrem(f'new_tickets_{call.from_user.id}', 0, ticket_num)
        logger.info(f'The user {call.from_user.id} has been accepted ticket: {ticket_num}')
        msg = await create_ticket_msg(ticket_data)
        await call.message.edit_text(text=msg.msg, reply_markup=msg.keyboard)
        await call.answer(f'Notification disabled for ticket: {ticket_num}')
        logger.info(f'The user {call.from_user.id} turned off the notification for ticket: {ticket_num}')
    else:
        field_value = ticket_data[field]
        if field_value:
            msg = await edit_ticket_msg(ticket_num, field, field_value)
            await call.message.edit_text(text=msg.msg, reply_markup=msg.keyboard)
            await call.answer()
        else:
            await call.answer('It is empty there')
