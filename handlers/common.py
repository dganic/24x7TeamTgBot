from aiogram import types
from aiogram.dispatcher.filters import CommandStart, IDFilter

from bot_loader import dp
from data.config import duty_team_ids, kb_main_buttons
from keyboards.kb_tickets import get_kb_main


@dp.message_handler(CommandStart(), IDFilter(user_id=duty_team_ids), state='*')
async def bot_start(message: types.Message):
    await message.answer(f'<b>{message.from_user.full_name}</b>, hello!\n\n'
                         f'I am your bot assistant', reply_markup=get_kb_main(kb_main_buttons))
