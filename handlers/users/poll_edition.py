from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default import main, question_type
from keyboards.inline.edit_poll import make_question_keyboard
from keyboards.inline.callback_data import poll_callback, add_question_callback, edit_poll_name_callback, \
    question_callback, delete_poll_callback, edit_poll_description_callback, finish_poll_creation_callback, \
    add_answer_callback, back_to_poll_callback, delete_question_callback, edit_question_callback, answer_callback
from keyboards.inline.edit_question import make_edit_question_keyboard

from loader import dp
import states

from utils.db_api.database import Poll, Question, Answer


@dp.callback_query_handler(poll_callback.filter())
async def bot_poll_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    questions = await Question.filter(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))


@dp.callback_query_handler(back_to_poll_callback.filter())
async def bot_back_to_poll_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    questions = await Question.filter(Question.poll_id == poll.id)

    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))


@dp.callback_query_handler(delete_poll_callback.filter())
async def bot_delete_poll_callback(call: CallbackQuery, callback_data: dict):
    await Poll.delete.where(Poll.id == int(callback_data['poll_id'])).gino.status()
    await call.message.delete()
    await call.message.answer(text="Опрос удален", reply_markup=main.mainMenu)


@dp.callback_query_handler(delete_question_callback.filter())
async def bot_delete_question_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.get(Question.id == int(callback_data['question_id']))
    poll_id = question.poll_id
    await Question.delete.where(Question.id == int(callback_data['question_id'])).gino.status()

    poll = await Poll.get(Poll.id == poll_id)
    questions = await Question.filter(Question.poll_id == poll.id)
    await call.message.edit_text(text=str(poll),
                                 reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))


@dp.callback_query_handler(answer_callback.filter())
async def bot_delete_answer_callback(call: CallbackQuery, callback_data: dict):
    answer = await Answer.get(Answer.id == int(callback_data['answer_id']))
    question_id = answer.question_id
    await Answer.delete.where(Answer.id == int(callback_data['answer_id'])).gino.status()

    question = await Question.get(Question.id == question_id)
    answers = await Answer.filter(Answer.question_id == question.id)
    await call.message.edit_text(text="Вопрос: " + question.text,
                                 reply_markup=make_edit_question_keyboard(answers=answers,
                                                                          poll_id=int(question.poll_id),
                                                                          question_id=int(question.id),
                                                                          type_id=question.type_id))


@dp.callback_query_handler(finish_poll_creation_callback.filter())
async def bot_finish_poll_creation_callback(call: CallbackQuery, callback_data: dict):
    
    await call.message.delete()
    await call.message.answer(text="Завершено.", reply_markup=main.mainMenu)


@dp.callback_query_handler(question_callback.filter())
async def bot_question_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.get(Question.id == int(callback_data['question_id']))
    answers = await Answer.filter(Answer.question_id == question.id)
    await call.message.edit_text(text="Вопрос: " + question.text,
                                 reply_markup=make_edit_question_keyboard(answers=answers,
                                                                          poll_id=int(question.poll_id),
                                                                          question_id=int(question.id),
                                                                          type_id=question.type_id))


# change poll name
@dp.callback_query_handler(edit_poll_name_callback.filter())
async def bot_edit_poll_name_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(poll_id=callback_data['poll_id'], message_to_delete_id=call.message.message_id)
    await states.change_poll_name.ChangePollName.name.set()
    await call.message.answer(text='Введите новое название для теста')


@dp.message_handler(state=states.change_poll_name.ChangePollName.name)
async def process_change_poll_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    poll = await Poll.get(Poll.id == int(data['poll_id']))
    await poll.update(name=data['name']).apply()

    questions = await Question.filter(Question.poll_id == poll.id)
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text=str(poll), reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))

    await state.finish()


# change poll description
@dp.callback_query_handler(edit_poll_description_callback.filter())
async def bot_edit_poll_description_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(poll_id=callback_data['poll_id'], message_to_delete_id=call.message.message_id)
    await states.change_poll_description.ChangePollDescription.description.set()
    await call.message.answer(text='Введите новое описание для теста')


@dp.message_handler(state=states.change_poll_description.ChangePollDescription.description)
async def process_change_poll_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    poll = await Poll.get(Poll.id == int(data['poll_id']))
    await poll.update(description=data['description']).apply()

    questions = await Question.filter(Question.poll_id == poll.id)
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text=str(poll), reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))

    await state.finish()


# add question
@dp.callback_query_handler(add_question_callback.filter())
async def bot_add_question_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(poll_id=callback_data['poll_id'], message_to_delete_id=call.message.message_id)
    await states.create_question.CreateQuestion.text.set()
    await call.message.answer(text='Введите текст вопроса')


@dp.message_handler(state=states.create_question.CreateQuestion.text)
async def process_add_question_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await states.create_question.CreateQuestion.next()
    await message.reply(text="Выберите тип вопроса:", reply_markup=question_type.typeQuestionMenu)


@dp.message_handler(state=states.create_question.CreateQuestion.type)
async def process_add_question_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text

    if data['type'] == "1. Один вариант ответа":
        await Question.create(text=data['text'], type_id=1, poll_id=int(data['poll_id']))
        await message.answer(text='Создан вопрос с одним вариантом ответа.', reply_markup=types.ReplyKeyboardRemove())

    elif data['type'] == "2. Несколько вариантов ответа":
        await Question.create(text=data['text'], type_id=2, poll_id=int(data['poll_id']))
        await message.answer(text='Создан вопрос с несколькими вариантами ответа.',
                             reply_markup=types.ReplyKeyboardRemove())

    elif data['type'] == "3. Пользовательский вариант ответа":
        await Question.create(text=data['text'], type_id=3, poll_id=int(data['poll_id']))
        await message.answer(text='Создан вопрос с пользовательским ответом.', reply_markup=types.ReplyKeyboardRemove())

    else:
        await message.answer(text='Такого типа не существует!', reply_markup=types.ReplyKeyboardRemove())

    poll = await Poll.get(Poll.id == int(data['poll_id']))
    questions = await Question.filter(Question.poll_id == poll.id)

    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text=str(poll), reply_markup=make_question_keyboard(questions=questions, poll_id=poll.id))
    await state.finish()


# edit question
@dp.callback_query_handler(edit_question_callback.filter())
async def bot_edit_question_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(question_id=callback_data['question_id'], message_to_delete_id=call.message.message_id)
    await states.change_question_text.ChangeQuestionText.text.set()
    await call.message.answer(text='Введите новый текст для вопроса')


@dp.message_handler(state=states.change_question_text.ChangeQuestionText.text)
async def process_change_question_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    question = await Question.get(Question.id == int(data['question_id']))
    await question.update(text=data['text']).apply()
    answers = await Answer.filter(Answer.question_id == question.id)
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text="Вопрос: " + question.text,
                         reply_markup=make_edit_question_keyboard(answers=answers, poll_id=int(question.poll_id),
                                                                  question_id=int(question.id),
                                                                  type_id=question.type_id))
    await state.finish()


# add answer
@dp.callback_query_handler(add_answer_callback.filter())
async def bot_add_answer_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(question_id=callback_data['question_id'], message_to_delete_id=call.message.message_id)
    await states.create_answer.CreateAnswer.text.set()
    await call.message.answer(text='Введите текст ответа')


@dp.message_handler(state=states.create_answer.CreateAnswer.text)
async def process_add_answer_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    await Answer.create(text=data['text'], question_id=int(data['question_id']))

    question = await Question.get(Question.id == int(data['question_id']))
    answers = await Answer.filter(Answer.question_id == question.id)
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text="Вопрос: " + question.text,
                         reply_markup=make_edit_question_keyboard(answers=answers, poll_id=int(question.poll_id),
                                                                  question_id=int(question.id),
                                                                  type_id=question.type_id))
    await state.finish()
