from aiogram.dispatcher.filters.state import State, StatesGroup


class EnterUserAnswer(StatesGroup):
    message_to_delete_id = State()
    question_id = State()
    text = State()