from aiogram import md
from aiogram import types
from loguru import logger
from typing import NamedTuple

from data.config import kb_main_buttons
from keyboards.kb_tickets import get_kb_inl_ticket, get_kb_main


class AnswerMessages(NamedTuple):
    msg: str
    keyboard: types.InlineKeyboardMarkup


async def edit_ticket_msg(ticket_num: str, field: str, field_value: str):
    if len(field_value) > 4096:
        prep_msg = field_value[0:4096]
    else:
        prep_msg = field_value
    edited_ticket_msg = f"<pre>{md.quote_html(prep_msg)}</pre>\n\n" \
                        f"<b>{ticket_num}</b>"
    msg = AnswerMessages(msg=edited_ticket_msg, keyboard=get_kb_inl_ticket(ticket_num, field))
    return msg


async def create_ticket_msg(ticket_data: dict, accepted: bool = True):
    if ticket_data:
        ticket_type = ticket_data['sys_class_name']
        if ticket_type == 'Incident':
            ticket_msg = f"<b>{ticket_data['sys_class_name']}:</b> <code>{ticket_data['number']}</code>\n" \
                         f"<b>State:</b> <code>{ticket_data['state']}</code>\n" \
                         f"<b>Impact:</b> <code>{ticket_data['impact']}</code>\n" \
                         f"<b>Priority:</b> <code>{ticket_data['priority']}</code>\n" \
                         f"<b>Severity:</b> <code>{ticket_data['severity']}</code>\n" \
                         f"<b>Assignment group:</b> <code>{ticket_data['assignment_group']}</code>\n" \
                         f"<b>Assigned to:</b> <code>{ticket_data['assigned_to']}</code>\n\n" \
                         f"<b>Short description:</b>\n<pre>{ticket_data['short_description']}</pre>"
            logger.debug(f'Incident message:\n {ticket_msg}')
            return AnswerMessages(msg=ticket_msg, keyboard=get_kb_inl_ticket(ticket_data['number'], accepted=accepted))
        elif ticket_type == 'Catalog Task':
            ticket_msg = f"<b>{ticket_data['sys_class_name'].capitalize()}:</b> <code>{ticket_data['number']}</code>\n" \
                         f"<b>State:</b> <code>{ticket_data['state']}</code>\n" \
                         f"<b>Parent:</b> <code>{ticket_data['parent']}</code>\n" \
                         f"<b>Impact:</b> <code>{ticket_data['impact']}</code>\n" \
                         f"<b>Priority:</b> <code>{ticket_data['priority']}</code>\n" \
                         f"<b>Assignment group:</b> <code>{ticket_data['assignment_group']}</code>\n" \
                         f"<b>Assigned:</b> <code>{ticket_data['assigned_to']}</code>\n\n" \
                         f"<b>Short description:</b>\n<pre>{ticket_data['short_description']}</pre>"
            logger.debug(f'Task message:\n {ticket_msg}')
            return AnswerMessages(msg=ticket_msg, keyboard=get_kb_inl_ticket(ticket_data['number'], accepted=accepted))
        else:
            logger.debug(f'No tickets in the stack')
            return AnswerMessages(msg='No tickets in the stack', keyboard=get_kb_main(kb_main_buttons))
