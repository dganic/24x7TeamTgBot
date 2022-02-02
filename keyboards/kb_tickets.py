from aiogram import types
from loguru import logger
from aiogram.utils.callback_data import CallbackData

cb_ticket_data = CallbackData('ticket_data', 'action', 'ticket_number')


def get_kb_main(buttons):
    logger.debug(buttons)
    kb_repl_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        kb_repl_main.insert(button)
    logger.debug(kb_repl_main)
    return kb_repl_main


def get_kb_inl_ticket(ticket_num, field=None, accepted: bool = True):
    kb_inl_ticket_btn_1 = types.InlineKeyboardButton(text="Description",
                                                     callback_data=cb_ticket_data.new(action='description',
                                                                                      ticket_number=ticket_num))
    kb_inl_ticket_btn_2 = types.InlineKeyboardButton(text="Work notes",
                                                     callback_data=cb_ticket_data.new(action='comments_and_work_notes',
                                                                                      ticket_number=ticket_num))
    kb_inl_ticket_btn_3 = types.InlineKeyboardButton(text="Ticket",
                                                     callback_data=cb_ticket_data.new(action='ticket',
                                                                                      ticket_number=ticket_num))
    kb_inl_ticket_btn_4 = types.InlineKeyboardButton(text="Accepted",
                                                     callback_data=cb_ticket_data.new(action='accepted',
                                                                                      ticket_number=ticket_num))
    if not field:
        kb_inl_ticket = types.InlineKeyboardMarkup().insert(kb_inl_ticket_btn_1).insert(kb_inl_ticket_btn_2)
        if not accepted:
            kb_inl_ticket.add(kb_inl_ticket_btn_4)
    elif field == 'description':
        kb_inl_ticket = types.InlineKeyboardMarkup().insert(kb_inl_ticket_btn_3).insert(kb_inl_ticket_btn_2)
    elif field == 'comments_and_work_notes':
        kb_inl_ticket = types.InlineKeyboardMarkup().insert(kb_inl_ticket_btn_3).insert(kb_inl_ticket_btn_1)
    elif field == 'accepted':
        kb_inl_ticket = types.InlineKeyboardMarkup().insert(kb_inl_ticket_btn_1).insert(kb_inl_ticket_btn_2)
        kb_inl_ticket.add(kb_inl_ticket_btn_4)

    return kb_inl_ticket


