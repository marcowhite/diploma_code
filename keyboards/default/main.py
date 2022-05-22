from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# main menu

btnUse = KeyboardButton ('☑️ Пройти опрос')
btnPolls = KeyboardButton('📰 Мои опросы')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnUse,btnPolls)

