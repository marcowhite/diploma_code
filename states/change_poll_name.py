from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangePollName(StatesGroup):
    message_to_delete_id = State()
    poll_id = State()
    name = State()