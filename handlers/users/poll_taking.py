from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from keyboards.default import main, polls
from keyboards.inline.callback_data import start_poll_callback, pick_answer_callback, poll_taking_question_callback, \
    enter_user_answer_callback, finish_poll_callback
from keyboards.inline.take_poll import question_keyboard
from loader import dp
import states

from utils.db_api.database import Poll, UserPoll, Question, UserAnswer, Answer
from utils.misc.polls import get_prev_and_next_question_id


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
    userpoll = await UserPoll.get(UserPoll.poll_id == int(data['poll_id']))
    if poll:
        if userpoll:
            await message.reply(text=str(poll) + str(userpoll),
                                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                                    text="Перепройти опрос", callback_data=start_poll_callback.new(poll_id=poll.id))))
        else:
            await message.reply(text=str(poll), reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                text="Пройти опрос", callback_data=start_poll_callback.new(poll_id=poll.id))))
    else:
        await message.reply(text="Опроса с таким идентификатором не существует. Попробуйте снова!",
                            reply_markup=main.mainMenu)

    await state.finish()


@dp.callback_query_handler(start_poll_callback.filter())
async def bot_start_poll_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.get(Question.poll_id == int(callback_data['poll_id']))

    answers = await Answer.filter(Answer.question_id == question.id)
    questions = await Question.filter(Question.poll_id == question.poll_id, select_values=['id'])
    prev_question_id, next_question_id = get_prev_and_next_question_id(question_id=question.id, questions=questions)
    user_answer_ids = [user_answer_id[0] for user_answer_id in
                       await UserAnswer.filter(UserAnswer.user_id == call.from_user.id,
                                               UserAnswer.question_id == question.id, select_values=['answer_id'])]
    await call.message.edit_text(text=question.text,
                                 reply_markup=question_keyboard(poll_id=int(callback_data['poll_id']), answers=answers,
                                                                user_answer_ids=user_answer_ids,
                                                                prev_question_id=prev_question_id,
                                                                next_question_id=next_question_id,
                                                                question_type=question.type_id,
                                                                question_id=question.id,
                                                                ))


@dp.callback_query_handler(pick_answer_callback.filter())
async def bot_pick_answer_callback(call: CallbackQuery, callback_data: dict):
    answer = await Answer.get(Answer.id == int(callback_data['answer_id']))

    question = await Question.get(Question.id == answer.question_id)
    if question.type_id == 1:
        answers = await Answer.filter(Answer.question_id == question.id)
        for answer_for_check in answers:
            await UserAnswer.delete.where(UserAnswer.answer_id == answer_for_check.id).where(
                UserAnswer.user_id == call.from_user.id).gino.status()
        await UserAnswer.create(answer_id=answer.id, question_id=answer.question_id,
                                user_id=call.from_user.id)
    elif question.type_id == 2:
        answers = await Answer.filter(Answer.question_id == question.id)
        answer_for_check = await UserAnswer.get(UserAnswer.answer_id == answer.id,
                                                UserAnswer.user_id == call.from_user.id)
        if answer_for_check:
            await UserAnswer.delete.where(UserAnswer.answer_id == answer_for_check.answer_id).where(
                UserAnswer.user_id == call.from_user.id).gino.status()
        else:
            await UserAnswer.create(answer_id=answer.id, question_id=answer.question_id,
                                    user_id=call.from_user.id)
    else:
        user_answer = await UserAnswer.get(UserAnswer.question_id == question.id,
                                           UserAnswer.user_id == call.from_user.id)
        answers = await Answer.filter(Answer.id == user_answer.answer_id)
    questions = await Question.filter(Question.poll_id == question.poll_id, select_values=['id'])
    user_answer_ids = [user_answer_id[0] for user_answer_id in
                       await UserAnswer.filter(UserAnswer.user_id == call.from_user.id,
                                               UserAnswer.question_id == question.id, select_values=['answer_id'])]

    prev_question_id, next_question_id = get_prev_and_next_question_id(question_id=question.id, questions=questions)

    await call.message.edit_text(text=question.text,
                                 reply_markup=question_keyboard(poll_id=question.poll_id, answers=answers,
                                                                user_answer_ids=user_answer_ids,
                                                                prev_question_id=prev_question_id,
                                                                next_question_id=next_question_id,
                                                                question_type=question.type_id,
                                                                question_id=question.id,
                                                                ))


@dp.callback_query_handler(finish_poll_callback.filter())
async def bot_finish_poll_callback(call: CallbackQuery, callback_data: dict):
    userpoll = await UserPoll.create_or_update(poll_id=int(callback_data['poll_id']), user_id=call.from_user.id)
    await call.message.delete()
    await call.message.answer(text="Завершено.", reply_markup=main.mainMenu)


@dp.callback_query_handler(poll_taking_question_callback.filter())
async def bot_poll_taking_question_callback(call: CallbackQuery, callback_data: dict):
    question = await Question.get(Question.id == int(callback_data['question_id']))

    answers = await Answer.filter(Answer.question_id == question.id)
    questions = await Question.filter(Question.poll_id == question.poll_id, select_values=['id'])
    prev_question_id, next_question_id = get_prev_and_next_question_id(question_id=question.id, questions=questions)
    user_answer_ids = [user_answer_id[0] for user_answer_id in
                       await UserAnswer.filter(UserAnswer.user_id == call.from_user.id,
                                               UserAnswer.question_id == question.id, select_values=['answer_id'])]
    await call.message.edit_text(text=question.text,
                                 reply_markup=question_keyboard(poll_id=question.poll_id, answers=answers,
                                                                user_answer_ids=user_answer_ids,
                                                                prev_question_id=prev_question_id,
                                                                next_question_id=next_question_id,
                                                                question_type=question.type_id,
                                                                question_id=question.id,
                                                                ))


# enter user answer
@dp.callback_query_handler(enter_user_answer_callback.filter())
async def bot_enter_user_answer_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(question_id=callback_data['question_id'], message_to_delete_id=call.message.message_id)
    await states.enter_user_answer.EnterUserAnswer.text.set()
    await call.message.answer(text='Введите текст ответа')


@dp.message_handler(state=states.enter_user_answer.EnterUserAnswer.text)
async def process_enter_user_answer_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    question = await Question.get(Question.id == int(data['question_id']))
    answer = await Answer.create(text=data['text'], question_id=question.id)
    await UserAnswer.create(question_id=question.id, answer_id=answer.id, user_id=message.from_user.id)

    answers = await Answer.filter(Answer.id == answer.id)
    questions = await Question.filter(Question.poll_id == question.poll_id, select_values=['id'])
    prev_question_id, next_question_id = get_prev_and_next_question_id(question_id=question.id, questions=questions)
    user_answer_ids = [user_answer_id[0] for user_answer_id in
                       await UserAnswer.filter(UserAnswer.user_id == message.from_user.id,
                                               UserAnswer.question_id == question.id, select_values=['answer_id'])]
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
    await message.answer(text=question.text,
                         reply_markup=question_keyboard(poll_id=question.poll_id, answers=answers,
                                                        user_answer_ids=user_answer_ids,
                                                        prev_question_id=prev_question_id,
                                                        next_question_id=next_question_id,
                                                        question_type=question.type_id,
                                                        question_id=question.id,
                                                        ))

    await state.finish()
