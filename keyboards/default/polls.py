from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# polls menu

btnGoMain = KeyboardButton('⬅️ В главное меню')
btnCompleted = KeyboardButton('📜 Пройденные опросы')
btnCreate = KeyboardButton('🆕 Создать опрос')
btnStats = KeyboardButton('ℹ️ Статистика опросов')

pollsMenu = ReplyKeyboardMarkup(resize_keyboard=True).row(btnCompleted, btnCreate)
pollsMenu.row(btnStats)
pollsMenu.row(btnGoMain)