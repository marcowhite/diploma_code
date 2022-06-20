from typing import List

from utils.db_api.database import Poll, Question, Answer, UserAnswer, User

async def get_poll_result_text(poll: str,username: str, questions: List[Question]):
    message_text = poll
    message_text += "Имя пользователя: @" + username + "\n"
    for question in questions:
        message_text += "\n<b>" + question.text + "</b>"
        answers = await Answer.filter(Answer.question_id == question.id)
        for answer in answers:
            user_answer = await UserAnswer.get(UserAnswer.answer_id == answer.id)
            if user_answer:
                message_text += "\n" + answer.text
                # message_text += " ☑️"
        message_text += "\n"

    return message_text