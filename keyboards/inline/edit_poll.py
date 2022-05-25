from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


editPoll = InlineKeyboardMarkup(row_width=1)

btnAddQuestion = InlineKeyboardButton(text="Добавить вопрос", callback_data='btnAddQuestion')
btnEditName = InlineKeyboardButton(text="Изменить название", callback_data='btnEditName')
btnEditDescription = InlineKeyboardButton(text="Изменить описание", callback_data='btnEditDescription')

editPoll.insert(btnAddQuestion)
editPoll.insert(btnEditName)
editPoll.insert(btnEditDescription)
