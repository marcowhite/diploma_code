from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.default import main, polls
from loader import dp
import states

from utils.db_api.database import Poll

@dp.message_handler(text="📰 Мои опросы")
async def command_my_polls(message: types.Message):
    await message.answer("Переходим в мои опросы", reply_markup=polls.pollsMenu)

@dp.message_handler(text="⬅️ В главное меню")
async def command_go_main(message: types.Message):
    await message.answer("Переходим в главное меню", reply_markup=main.mainMenu)

@dp.message_handler(text="🆕 Создать опрос")
async def command_create_poll(message: types.Message):

    await states.create_poll.CreatePoll.name.set()
    await message.reply("Введите название опроса")

@dp.message_handler(text="☑️ Пройти опрос")
async def command_menus(message: types.Message):
    await states.take_poll.TakePoll.id.set()
    await message.reply("Введите ID опроса")

@dp.message_handler(text="ℹ️ Статистика опросов")
async def command_menus(message: types.Message):
    data = await Poll.filter(Poll.user_id==message.from_user.id)
    await message.answer(data, reply_markup=main.mainMenu)



@dp.message_handler(state = states.create_poll.CreatePoll.name)
async def process_translation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await states.create_poll.CreatePoll.next()
    await message.reply("Введите описание")


@dp.message_handler(state = states.create_poll.CreatePoll.description)
async def process_translation(message: types.Message, state: FSMContext):
    await states.create_poll.CreatePoll.next()

    async with state.proxy() as data:
        data['description'] = message.text

    # await psycopg.commit_poll(name=data['name'], description=data['description'], owner_id=message.from_user.id)

    await message.reply('Завершено.', reply_markup=polls.pollsMenu)
    await state.finish()


@dp.message_handler(state = states.take_poll.TakePoll.id)
async def process_translation(message: types.Message, state: FSMContext):
    await states.take_poll.TakePoll.next()

    async with state.proxy() as data:
        data['id'] = message.text

    await message.reply('Завершено.', reply_markup=main.mainMenu)

    await state.finish()
