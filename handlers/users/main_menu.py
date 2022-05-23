from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import main, polls
from loader import dp
import states

from utils.db_api.database import Poll, UserPoll


@dp.message_handler(text="📰 Мои опросы")
async def command_my_polls(message: types.Message):
    await message.answer("Переходим в 📰 Мои опросы", reply_markup=polls.pollsMenu)


@dp.message_handler(text="⬅️ В главное меню")
async def command_go_main(message: types.Message):
    await message.answer("Переходим в ⬅️ В главное меню", reply_markup=main.mainMenu)


@dp.message_handler(text="🆕 Создать опрос")
async def command_create_poll(message: types.Message):
    await states.create_poll.CreatePoll.name.set()
    await message.reply("Введите название опроса:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(text="☑️ Пройти опрос")
async def command_take_poll(message: types.Message):
    await states.take_poll.TakePoll.id.set()
    await message.reply("Введите ID опроса:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(text="ℹ️ Статистика опросов")
async def command_poll_stats(message: types.Message):
    polls = await Poll.filter(Poll.user_id == int(message.from_user.id))
    for poll in polls:
        await message.answer("ID: " + str(poll.id) +
                             "\nНазвание: " + poll.name +
                             "\nОписание: " + poll.description)


@dp.message_handler(text="📜 Пройденные опросы")
async def command_poll_completed(message: types.Message):
    userpolls = await UserPoll.filter(UserPoll.user_id == int(message.from_user.id))

    for userpoll in userpolls:
        poll = await Poll.get(Poll.id == userpoll.poll_id)
        await message.answer("ID: " + str(poll.id) +
                             "\nНазвание: " + poll.name +
                             "\nОписание: " + poll.description +
                             "\nДата прохождения: " + userpoll.time_updated
                             )


@dp.message_handler(state=states.create_poll.CreatePoll.name)
async def process_create_poll_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await states.create_poll.CreatePoll.next()
    await message.reply("Введите описание:")


@dp.message_handler(state=states.create_poll.CreatePoll.description)
async def process_create_poll_description(message: types.Message, state: FSMContext):
    await states.create_poll.CreatePoll.next()

    async with state.proxy() as data:
        data['description'] = message.text
    await Poll.create(name=data['name'], description=data['description'], user_id=message.from_user.id)

    await message.reply('Завершено.', reply_markup=polls.pollsMenu)
    await state.finish()


@dp.message_handler(state=states.take_poll.TakePoll.id)
async def process_take_poll(message: types.Message, state: FSMContext):
    await states.take_poll.TakePoll.next()

    async with state.proxy() as data:
        data['id'] = message.text

    poll = await Poll.get(Poll.id == int(data['id']))
    await UserPoll.create(poll_id=int(data['id']), user_id=message.from_user.id)
    await message.reply('Завершено. ' +
                        "\nID: " + str(poll.id) +
                        "\nНазвание: " + poll.name +
                        "\nОписание: " + poll.description, reply_markup=main.mainMenu)
    await state.finish()
