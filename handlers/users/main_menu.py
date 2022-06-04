from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default import main, polls
from keyboards.inline.callback_data import stat_poll_callback
from loader import dp

from utils.db_api.database import Poll, UserPoll


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
            await message.answer(poll, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                text="Показать статистику", callback_data=stat_poll_callback.new(poll_id=poll.id))))
    else:
        await message.answer('У вас нет опросов!')


@dp.message_handler(text="📜 Пройденные опросы")
async def command_poll_completed(message: types.Message):
    userpolls = await UserPoll.filter(UserPoll.user_id == int(message.from_user.id))

    for userpoll in userpolls:
        poll = await Poll.get(Poll.id == userpoll.poll_id)
        await message.answer(str(poll) + str(userpoll), reply_markup=main.mainMenu)
