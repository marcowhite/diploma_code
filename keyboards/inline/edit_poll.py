from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_data import question_callback, add_question_callback, edit_poll_name_callback, \
    edit_poll_description_callback
from utils.db_api.database import Question


def make_question_keyboard(questions: List[Question], poll_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if questions:
        for question in questions:
            button_text = question.text
            keyboard.add(
                InlineKeyboardButton(text=button_text, callback_data=question_callback.new(question_id=question.id))
            )

    keyboard.add(
        InlineKeyboardButton(text='Добавить вопрос', callback_data=add_question_callback.new(poll_id=poll_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Изменить название", callback_data=edit_poll_name_callback.new(poll_id=poll_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Изменить описание", callback_data=edit_poll_description_callback.new(poll_id=poll_id))
    )

    return keyboard
