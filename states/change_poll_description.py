from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangePollDescription(StatesGroup):
    message_to_delete_id = State()
    poll_id = State()
    description = State()