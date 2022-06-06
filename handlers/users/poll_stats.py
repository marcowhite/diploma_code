from keyboards.inline.callback_data import stat_poll_callback, pick_user_poll_callback
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.edit_question import make_edit_question_keyboard

from loader import dp

from utils.db_api.database import Poll, Question, Answer, UserPoll, User, UserAnswer


@dp.callback_query_handler(stat_poll_callback.filter())
async def bot_stat_poll_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    user_polls = await UserPoll.filter(UserPoll.poll_id == poll.id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    for user_poll in user_polls:
        user = await User.get(User.id == user_poll.user_id)
        keyboard.add(
            InlineKeyboardButton(
                text="@" + user.username,
                callback_data=pick_user_poll_callback.new(userpoll_id=user_poll.id)
            )
        )
    await call.message.edit_text(text=str(poll) + "\nСписок пользователей: ", reply_markup=keyboard)


@dp.callback_query_handler(pick_user_poll_callback.filter())
async def bot_pick_user_poll_callback(call: CallbackQuery, callback_data: dict):
    message_text = ""
    user_poll = await UserPoll.get(UserPoll.id == int(callback_data['userpoll_id']))
    poll = await Poll.get(Poll.id == user_poll.poll_id)
    questions = await Question.filter(Question.poll_id == user_poll.poll_id)
    message_text = str(poll)
    for question in questions:
        message_text += "\n<b>" + question.text + "</b>"
        answers = await Answer.filter(Answer.question_id == question.id)
        for answer in answers:
            user_answer = await UserAnswer.get(UserAnswer.answer_id == answer.id)
            message_text += "\n " + answer.text
            if user_answer:
                message_text += " ☑️"
    user = await User.get(User.id == user_poll.user_id)

    await call.message.answer(text=message_text)
