from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateAnswer(StatesGroup):
    message_to_delete_id = State()
    question_id = State()
    text = State()