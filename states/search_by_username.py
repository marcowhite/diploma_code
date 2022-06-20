from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchUserName(StatesGroup):
    message_to_delete_id = State()
    poll_id = State()
    username = State()