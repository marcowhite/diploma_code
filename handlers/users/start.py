from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.poll_taking import process_take_poll
from keyboards.default import main
from loader import dp
from utils.db_api.database import User


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await User.get_by_id_or_create(id=message.from_user.id, full_name=message.from_user.full_name,
                                   username=message.from_user.username)
    await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=main.mainMenu)
    poll_id = message.get_args()
    if poll_id:
        state = dp.current_state()
        message.text=poll_id
        await process_take_poll(message=message,state=state)
