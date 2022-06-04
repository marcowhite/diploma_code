from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_api.database import Answer, UserAnswer

from keyboards.inline.callback_data import answer_callback, back_to_poll_callback, edit_question_callback, \
    add_answer_callback, delete_question_callback, edit_question_type_callback, pick_answer_callback


def make_take_poll_keyboard(answers: List[Answer], user_answers: List[UserAnswer], question_id: int, type_id: int):

    keyboard = InlineKeyboardMarkup(row_width=2)

    if answers:
        count = 1
        for answer in answers:
            button_text = ""
            # if user_answers()
            button_text += str(count) + ". "
            button_text += answer.text
            keyboard.add(
                InlineKeyboardButton(text=button_text, callback_data=pick_answer_callback.new(answer_id=answer.id))
            )
            count += 1

    return keyboard
