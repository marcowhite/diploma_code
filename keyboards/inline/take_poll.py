from typing import List, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_api.database import Answer, UserAnswer

from keyboards.inline.callback_data import answer_callback, back_to_poll_callback, edit_question_callback, \
    add_answer_callback, delete_question_callback, pick_answer_callback, \
    finish_poll_callback, poll_taking_question_callback, start_poll_callback, enter_user_answer_callback, \
    delete_answer_created_by_user_callback


def question_keyboard(
        poll_id: int, answers: List[Answer], user_answer_ids: List[int], prev_question_id: int, next_question_id: int,
        is_passed: bool, question_type: int, question_id: int
):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if question_type == 2:
        for answer in answers:
            if answer.id in user_answer_ids:
                button_text = f"☑️  {answer.text}"
            else:
                button_text = f"🔲 {answer.text}"
            keyboard.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=pick_answer_callback.new(answer_id=answer.id)
                )
            )
    elif question_type == 3:
        if not answers:
            keyboard.add(
                InlineKeyboardButton(
                    text='Нажмите чтобы ввести ответ',
                    callback_data=enter_user_answer_callback.new(question_id=question_id)
                )
            )
        else:
            answer = answers.pop()
            button_text = "❌" + answer.text
            keyboard.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=delete_answer_created_by_user_callback.new(answer_id=answer.id)
                )
            )
    else:
        for answer in answers:
            if answer.id in user_answer_ids:
                button_text = f"☑️{answer.text}"
            else:
                button_text = answer.text
            keyboard.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=pick_answer_callback.new(answer_id=answer.id)
                )
            )

    nav_buttons = []
    if prev_question_id:
        nav_buttons.append(
            InlineKeyboardButton(text="🔙", callback_data=poll_taking_question_callback.new(question_id=prev_question_id))
        )
    else:
        nav_buttons.append(InlineKeyboardButton(text="🔙", callback_data=start_poll_callback.new(poll_id=poll_id)))
    if next_question_id:
        nav_buttons.append(
            InlineKeyboardButton(text="🔜", callback_data=poll_taking_question_callback.new(question_id=next_question_id))
        )
    elif not is_passed:
        nav_buttons.append(
            InlineKeyboardButton(text="🏁", callback_data=finish_poll_callback.new(poll_id=poll_id))
        )
    keyboard.row(*nav_buttons)

    return keyboard
