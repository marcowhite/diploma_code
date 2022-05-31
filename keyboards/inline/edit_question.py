from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_api.database import Answer

from keyboards.inline.callback_data import answer_callback, back_to_poll_callback, edit_question_callback, \
    add_answer_callback, delete_question_callback


def make_edit_question_keyboard(answers: List[Answer], poll_id: int, question_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if answers:
        count = 1
        for answer in answers:
            button_text = str(count) + ". "
            button_text += answer.text
            keyboard.add(
                InlineKeyboardButton(text=button_text, callback_data=answer_callback.new(answer_id=answer.id))
            )
            count += 1
    keyboard.add(
        InlineKeyboardButton(text="Изменить текст вопроса", callback_data=edit_question_callback(question_id=question_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Изменить тип вопроса", callback_data=edit_question_callback(question_id=question_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Добавить ответ", callback_data=add_answer_callback(question_id=question_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Удалить вопрос", callback_data=delete_question_callback(poll_id=poll_id))
    )
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data=back_to_poll_callback.new(poll_id=poll_id))
    )

    return keyboard
