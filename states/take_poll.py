from aiogram.dispatcher.filters.state import State, StatesGroup


class TakePoll(StatesGroup):
    poll_id = State()
