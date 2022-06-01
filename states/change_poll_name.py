from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangePollName(StatesGroup):
    name = State()