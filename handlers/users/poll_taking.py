from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from keyboards.default import main, polls
from keyboards.inline.callback_data import start_poll_callback
from loader import dp
import states

from utils.db_api.database import Poll, UserPoll, Question


@dp.message_handler(text="☑️ Пройти опрос")
async def command_take_poll(message: types.Message):
    await states.take_poll.TakePoll.poll_id.set()
    await message.reply("Введите ID опроса:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=states.take_poll.TakePoll.poll_id)
async def process_take_poll(message: types.Message, state: FSMContext):
    await states.take_poll.TakePoll.next()

    async with state.proxy() as data:
        data['poll_id'] = message.text

    poll = await Poll.get(Poll.id == int(data['poll_id']))
    if poll:
        await message.reply(text=str(poll), reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
            text="Пройти опрос", callback_data=start_poll_callback.new(poll_id=poll.id))))
    else:
        await message.reply(text="Опроса с таким идентификатором не существует. Попробуйте снова!",
                            reply_markup=main.mainMenu)

    # userpoll = await UserPoll.create_or_update(poll_id=int(data['id']), user_id=message.from_user.id)

    await state.finish()


@dp.callback_query_handler(start_poll_callback.filter())
async def bot_start_poll_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    questions = await Question.filter(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))
