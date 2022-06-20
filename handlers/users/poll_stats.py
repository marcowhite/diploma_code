from aiogram import types
from aiogram.dispatcher import FSMContext

import states.search_by_username
from keyboards.inline.callback_data import stat_poll_callback, pick_user_poll_callback, search_by_username_callback, \
    back_to_poll_stats_callback, delete_poll_callback, share_poll_callback
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.edit_poll import make_poll_stats_keyboard
from loader import dp

from utils.db_api.database import Poll, Question, Answer, UserPoll, User, UserAnswer
from utils.misc.poll_result import get_poll_result_text


@dp.callback_query_handler(stat_poll_callback.filter())
async def bot_stat_poll_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    user_polls = await UserPoll.filter(UserPoll.poll_id == poll.id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Найти по имени пользователя",
                             callback_data=search_by_username_callback.new(poll_id=poll.id))
    )
    for user_poll in user_polls:
        user = await User.get(User.id == user_poll.user_id)
        keyboard.add(
            InlineKeyboardButton(
                text="@" + user.username,
                callback_data=pick_user_poll_callback.new(userpoll_id=user_poll.id)
            )
        )
    keyboard.add(
        InlineKeyboardButton(text="Назад",
                             callback_data=back_to_poll_stats_callback.new(poll_id=poll.id))
    )
    await call.message.edit_text(text=str(poll) + "\nСписок пользователей: ", reply_markup=keyboard)


@dp.callback_query_handler(pick_user_poll_callback.filter())
async def bot_pick_user_poll_callback(call: CallbackQuery, callback_data: dict):
    user_poll = await UserPoll.get(UserPoll.id == int(callback_data['userpoll_id']))
    poll = await Poll.get(Poll.id == user_poll.poll_id)
    questions = await Question.filter(Question.poll_id == user_poll.poll_id)
    user = await User.get(User.id == user_poll.user_id)
    message_text = await get_poll_result_text(poll=str(poll), username=str(user.username), questions=questions)

    await call.message.answer(text=message_text)


@dp.callback_query_handler(share_poll_callback.filter())
async def bot_share_poll_callback(call: CallbackQuery, callback_data: dict):
    message_text = "t.me/poll_generator_bot?start=" + callback_data['poll_id']
    await call.message.answer(text=message_text)


@dp.callback_query_handler(back_to_poll_stats_callback.filter())
async def bot_back_to_poll_stats_callback(call: CallbackQuery, callback_data: dict):
    poll = await Poll.get(Poll.id == int(callback_data['poll_id']))
    await call.message.edit_text(poll, reply_markup=make_poll_stats_keyboard(poll_id=poll.id))


# search by username
@dp.callback_query_handler(search_by_username_callback.filter())
async def bot_search_by_username_callback(call: CallbackQuery, callback_data: dict):
    state = dp.current_state(user=call.from_user.id)
    await state.update_data(poll_id=callback_data['poll_id'], message_to_delete_id=call.message.message_id)
    await states.search_by_username.SearchUserName.username.set()
    await call.message.answer(text='Введите имя пользователя:')


@dp.message_handler(state=states.search_by_username.SearchUserName.username)
async def process_change_poll_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text

    poll = await Poll.get(Poll.id == int(data['poll_id']))
    user = await User.get(User.username == data['username'])
    if user:
        user_poll = await UserPoll.get(UserPoll.user_id == user.id, UserPoll.poll_id == poll.id)
        if user_poll:
            poll = await Poll.get(Poll.id == user_poll.poll_id)
            questions = await Question.filter(Question.poll_id == user_poll.poll_id)
            message_text = await get_poll_result_text(poll=str(poll), username=str(user.username), questions=questions)
            await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
            await message.answer(text=message_text)
        else:
            await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
            await message.answer(text='Пользователь с таким именем не проходил этот опрос!')
    else:
        await dp.bot.delete_message(chat_id=message.from_user.id, message_id=int(data['message_to_delete_id']))
        await message.answer(text='Данного пользователя нет в базе данных бота!')
    await state.finish()
