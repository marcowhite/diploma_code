from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.default import main, polls
from loader import dp
import states


@dp.message_handler()
async def command_menus(message: types.Message):
    if message.text == '📰 Мои опросы':
        await message.answer(message.text, reply_markup=main.mainMenu)

    elif message.text == '⬅️ В главное меню':
        await message.answer(message.text, reply_markup=main.mainMenu)

    elif message.text == '🆕 Создать опрос':
        await states.create_poll.CreatePoll.name.set()
        await message.reply("Введите название опроса")

    elif message.text == '☑️ Пройти опрос':
        await states.take_poll.TakePoll.id.set()
        await message.reply("Введите ID опроса")

    elif message.text == 'ℹ️ Статистика опросов':
        #data = await psycopg.get_polls(message.from_user.id)
        await message.answer(message.text, reply_markup=main.mainMenu)

    else:
        await message.answer(message.text, reply_markup=main.mainMenu)


@dp.message_handler(state=states.create_poll.CreatePoll.name)
async def process_translation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await states.create_poll.CreatePoll.next()
    await message.reply("Введите описание")


@dp.message_handler(state=states.create_poll.CreatePoll.description)
async def process_translation(message: types.Message, state: FSMContext):
    await states.create_poll.CreatePoll.next()

    async with state.proxy() as data:
        data['description'] = message.text

    # await psycopg.commit_poll(name=data['name'], description=data['description'], owner_id=message.from_user.id)

    await message.reply('Завершено.', reply_markup=polls.pollsMenu)
    await state.finish()


@dp.message_handler(state=states.take_poll.TakePoll.id)
async def process_translation(message: types.Message, state: FSMContext):
    await states.take_poll.TakePoll.next()

    async with state.proxy() as data:
        data['id'] = message.text

    await message.reply('Завершено.', reply_markup=main.mainMenu)

    await state.finish()
