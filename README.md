# diploma_code

Code part of my university diploma.

Made using Aiogram + GINO + SQLAlchemy + PostgreSQL stack.
## Features
With this bot you can:
- Make and edit poll
  - Create a poll with specified name and description
  - Change a poll name and description in case of mistake
  - Delete a poll
  - Create 3 types of questions: single answer, multiple answers and an answer entered by user
  - Change and delete question
  - Add and delete answers to the questions
- Take a poll by id
  - Select answers
  - Enter and delete user answer
  - Change your answers after compltion
- Get user answers for your poll in stats menu

Some of the features like poll editing after creation were left behind to maintain data integrity. Perhaps in future updates those shortcomings may disappear.
## To launch the rocket add .env with:
```
ADMINS=admin_id
BOT_TOKEN=bot_token
ip=db_ip
DATABASE_URL = postgres://user:password@db_ip:port/db_name
```
