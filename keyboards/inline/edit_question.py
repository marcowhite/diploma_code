from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


editQuestion = InlineKeyboardMarkup(row_width=1)

btnEditQuestion = InlineKeyboardButton(text="Изменить текст вопроса", callback_data='btnEditQuestion')
btnAddAnswer = InlineKeyboardButton(text="Добавить ответ", callback_data='btnAddAnswer')
btnDeleteQuestion = InlineKeyboardButton(text="Удалить вопрос", callback_data='btnDeleteQuestion')
btnGoBackToPoll = InlineKeyboardButton(text="Назад", callback_data='btnGoBackToPoll')

editQuestion.insert(btnEditQuestion)
editQuestion.insert(btnAddAnswer)
editQuestion.insert(btnDeleteQuestion)
editQuestion.insert(btnGoBackToPoll)