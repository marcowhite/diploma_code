from aiogram.dispatcher.filters.state import State, StatesGroup


class CreatePoll(StatesGroup):
    name = State()
    description = State()