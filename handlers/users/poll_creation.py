from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default import main, polls
from keyboards.inline.edit_poll import make_question_keyboard
from keyboards.inline.callback_data import poll_callback, add_question_callback, edit_poll_name_callback, \
    question_callback, delete_poll_callback
from keyboards.inline.edit_question import make_edit_question_keyboard

from loader import dp
import states

from utils.db_api.database import Poll, Question, Answer


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
    questions = await Question.get(Question.poll_id == poll.id)

    await message.reply('Завершено.\n' + str(poll),
                        reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))
    await state.finish()


@dp.callback_query_handler(poll_callback.filter())
async def bot_polls_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    questions = await Question.get(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))


@dp.callback_query_handler(add_question_callback.filter())
async def bot_add_question_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.create(text="Введите текст вопроса", type_id=1, poll_id=int(callback_data['poll_id']))
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    questions = await Question.filter(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))


@dp.callback_query_handler(delete_poll_callback.filter())
async def bot_add_question_callback(call: CallbackQuery, callback_data: dict):
    await Poll.delete.where(Poll.id==int(callback_data['poll_id'])).gino.status()
    await call.message.delete()


@dp.callback_query_handler(question_callback.filter())
async def bot_add_question_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.get(Question.id == int(callback_data['question_id']))
    answers = await Answer.filter(Answer.question_id == question.id)
    await call.message.edit_text(text=question.text,
                                 reply_markup=make_edit_question_keyboard(answers=answers,
                                                                          poll_id=int(question.poll_id),
                                                                          question_id=int(question.id)))


@dp.callback_query_handler(edit_poll_name_callback.filter())
async def bot_edit_poll_name_callback(call: CallbackQuery, callback_data: dict):
    await states.change_poll_name.ChangePollName.name.set()  # zdes edit
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))

    questions = await Question.filter(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))
