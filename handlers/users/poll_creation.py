from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import main, polls
from keyboards.inline import edit_question,edit_poll

from loader import dp
import states

from utils.db_api.database import Poll, UserPoll


@dp.message_handler(text="🆕 Создать опрос")
async def command_create_poll(message: types.Message):
    await states.create_poll.CreatePoll.name.set()
    await message.reply("Введите название опроса:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=states.create_poll.CreatePoll.name)
async def process_create_poll_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await states.create_poll.CreatePoll.next()
    await message.reply("Введите описание:")


@dp.message_handler(state=states.create_poll.CreatePoll.description)
async def process_create_poll_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    poll = await Poll.create(name=data['name'], description=data['description'], user_id=message.from_user.id)

    await states.create_poll.CreatePoll.next()
    await message.reply(str(poll), reply_markup=edit_poll.editPoll)


@dp.message_handler(state=states.create_poll.CreatePoll.poll_edition)
async def process_edit_poll(message: types.Message, state: FSMContext):

    await message.reply('Завершено.', reply_markup=main.mainMenu)
    await state.finish()