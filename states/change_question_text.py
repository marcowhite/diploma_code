from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangeQuestionText(StatesGroup):
    message_to_delete_id = State()
    question_id = State()
    text = State()