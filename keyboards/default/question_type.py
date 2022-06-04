from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


# question creation menu

btnTypeOne = KeyboardButton('1. Один вариант ответа')
btnTypeTwo = KeyboardButton('2. Несколько вариантов ответа')
btnTypeThree = KeyboardButton('3. Пользовательский вариант ответа')
typeQuestionMenu = ReplyKeyboardMarkup(resize_keyboard=True).row(btnTypeOne)
typeQuestionMenu.row(btnTypeTwo)
typeQuestionMenu.row(btnTypeThree)


# question menu

btnGoBack = KeyboardButton('⬅️')
btnGoForward = KeyboardButton('➡️')
questionMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnGoBack, btnGoForward)
