from aiogram.utils.callback_data import CallbackData


# poll callbacks

polls_callback = CallbackData("polls")
poll_callback = CallbackData("poll", "poll_id")
edit_poll_description_callback = CallbackData("poll", "poll_id")
edit_poll_name_callback = CallbackData("poll", "poll_id")

start_poll_callback = CallbackData("start_poll", "poll_id")
finish_poll_callback = CallbackData("finish_poll", "poll_id")
back_to_poll_callback = CallbackData("back_to_poll", "poll_id")

check_poll_results_callback = CallbackData("check_poll_results", "poll_id")

# questions callbacks

question_callback = CallbackData("question", "question_id")
edit_question_callback = CallbackData("edit_question", "question_id")
edit_question_type_callback = CallbackData("edit_question_type", "question_id")
delete_question_callback = CallbackData("delete_question_type", "poll_id")
add_question_callback = CallbackData("add_question", "poll_id")

# answer callbacks

answer_callback = CallbackData("answer", "answer_id")
add_answer_callback = CallbackData("add_answer", "answer_id")

