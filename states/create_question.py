from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateQuestion(StatesGroup):
    message_to_delete_id = State()
    poll_id = State()
    text = State()
    type = State()