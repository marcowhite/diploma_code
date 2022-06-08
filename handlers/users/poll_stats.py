from keyboards.inline.callback_data import stat_poll_callback, pick_user_poll_callback
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

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
    user_poll = await UserPoll.get(UserPoll.id == int(callback_data['userpoll_id']))
    poll = await Poll.get(Poll.id == user_poll.poll_id)
    questions = await Question.filter(Question.poll_id == user_poll.poll_id)
    user = await User.get(User.id == user_poll.user_id)
    message_text = str(poll)
    message_text += "Имя пользователя: @" + user.username + "\n"
    for question in questions:
        message_text += "\n<b>" + question.text + "</b>"
        answers = await Answer.filter(Answer.question_id == question.id)
        for answer in answers:
            user_answer = await UserAnswer.get(UserAnswer.answer_id == answer.id)
            if user_answer:
                message_text += "\n" + answer.text + "\n"
                # message_text += " ☑️"

    await call.message.answer(text=message_text)
