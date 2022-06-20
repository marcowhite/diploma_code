from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default import main, polls
from keyboards.inline.callback_data import stat_poll_callback, delete_poll_callback, share_poll_callback
from keyboards.inline.edit_poll import make_poll_stats_keyboard
from loader import dp

from utils.db_api.database import Poll, UserPoll, Question, User
from utils.misc.poll_result import get_poll_result_text


@dp.message_handler(text="📰 Мои опросы")
async def command_my_polls(message: types.Message):
    await message.answer("Переходим в 📰 Мои опросы", reply_markup=polls.pollsMenu)


@dp.message_handler(text="⬅️ В главное меню")
async def command_go_main(message: types.Message):
    await message.answer("Переходим в ⬅️ В главное меню", reply_markup=main.mainMenu)


@dp.message_handler(text="ℹ️ Статистика опросов")
async def command_poll_stats(message: types.Message):
    polls = await Poll.filter(Poll.user_id == int(message.from_user.id))

    if polls:
        for poll in polls:

            await message.answer(poll, reply_markup=make_poll_stats_keyboard(poll_id=poll.id))
    else:
        await message.answer('У вас нет опросов!')


@dp.message_handler(text="📜 Пройденные опросы")
async def command_poll_completed(message: types.Message):
    user_polls = await UserPoll.filter(UserPoll.user_id == int(message.from_user.id))
    if user_polls:
        for user_poll in user_polls:
            poll = await Poll.get(Poll.id == user_poll.poll_id)
            questions = await Question.filter(Question.poll_id == user_poll.poll_id)
            user = await User.get(User.id == user_poll.user_id)
            message_text = await get_poll_result_text(poll=str(poll), username=str(user.username), questions=questions)
            await message.answer(message_text, reply_markup=main.mainMenu)
    else:
        await message.answer('Вы не проходили опросы!')