from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import main, polls
from loader import dp
import states

from utils.db_api.database import Poll, UserPoll


@dp.message_handler(text="☑️ Пройти опрос")
async def command_take_poll(message: types.Message):
    await states.take_poll.TakePoll.id.set()
    await message.reply("Введите ID опроса:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=states.take_poll.TakePoll.id)
async def process_take_poll(message: types.Message, state: FSMContext):
    await states.take_poll.TakePoll.next()

    async with state.proxy() as data:
        data['id'] = message.text

    poll = await Poll.get(Poll.id == int(data['id']))
    userpoll = await UserPoll.create_or_update(poll_id=int(data['id']), user_id=message.from_user.id)

    await message.reply('Завершено.\n' + str(poll) + str(userpoll), reply_markup=main.mainMenu)
    await state.finish()
