from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.exceptions import BotBlocked

from sqlalchemy import Column, Integer, String, Index, Sequence, ForeignKey, Boolean, and_, func, DateTime
from sqlalchemy import sql
from sqlalchemy.exc import InvalidRequestError

from gino import Gino

from data.config import DATABASE_URL

database = Gino()


class BaseModel(database.Model):
    query: sql.Select

    @classmethod
    async def get(cls, *args, select_values: list | tuple = ()):
        if select_values:
            return await cls.select(*select_values).where(and_(*args)).gino.first()
        return await cls.query.where(and_(*args)).gino.first()

    @classmethod
    async def filter(cls, *args, select_values: list | tuple = ()):
        if select_values:
            return await cls.select(*select_values).where(and_(*args)).gino.all()
        return await cls.query.where(and_(*args)).gino.all()

    @classmethod
    async def all(cls):
        return await cls.query.gino.all()

    @classmethod
    async def count(cls) -> int:
        return await database.func.count(cls.id).gino.scalar()


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    full_name = Column(String(256))
    username = Column(String(128))

    _idx = Index('user_id_index', 'id')

    @classmethod
    async def get_by_id_or_create(cls, id: int, **kwargs):
        obj = await cls.get(cls.id == id)
        if not obj:
            obj = await cls.create(id=id, **kwargs)
        return obj

    @staticmethod
    async def mailing(bot: Bot, text: str, keyboard: InlineKeyboardMarkup = None) -> int:
        count_users = 0
        for user in await User.query.gino.all():
            try:
                await bot.send_message(chat_id=user.id, text=text, reply_markup=keyboard)
                count_users += 1
            except BotBlocked:
                pass
        return count_users


class Poll(BaseModel):
    __tablename__ = 'polls'

    id = Column(Integer, Sequence('poll_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(64))
    description = Column(String(256))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    _idx = Index('poll_id_index', 'id')

    def __str__(self):
        obj = "ID: <code>" + str(self.id) + "</code>\n"
        obj += "Название опроса: " + self.name + "\n"
        obj += "Описание: " + self.description + "\n"
        return str(obj)


class Question(BaseModel):
    __tablename__ = 'questions'

    id = Column(Integer, Sequence('question_id_seq'), primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id', ondelete='CASCADE'))
    type_id = Column(Integer, ForeignKey('types.id', ondelete='CASCADE'))
    text = Column(String(256))

    _idx = Index('question_id_index', 'id')


class Type(BaseModel):
    __tablename__ = 'types'

    id = Column(Integer, Sequence('question_id_seq'), primary_key=True)
    text = Column(String(256))

    _idx = Index('type_id_index', 'id')

    @staticmethod
    async def init_types():
        types = await Type.filter()
        if not types:
            await Type.create(text="Один вариант ответа")
            await Type.create(text="Несколько вариантов ответа")
            await Type.create(text="Пользовательский вариант ответа")

class Answer(BaseModel):
    __tablename__ = 'answers'

    id = Column(Integer, Sequence('answer_id_seq'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    text = Column(String(256))

    _idx = Index('answer_id_index', 'id')


class UserAnswer(BaseModel):
    __tablename__ = 'user_answers'

    id = Column(Integer, Sequence('user_answer_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    answer_id = Column(Integer, ForeignKey('answers.id', ondelete='CASCADE'))

    _idx = Index('user_answer_id_index', 'id')


class UserPoll(BaseModel):
    __tablename__ = 'user_polls'

    id = Column(Integer, Sequence('user_answer_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    poll_id = Column(Integer, ForeignKey('polls.id', ondelete='CASCADE'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    async def create_or_update(cls, poll_id: int, user_id: int, **kwargs):
        obj = await cls.get(cls.poll_id == poll_id, cls.user_id == user_id)
        if not obj:
            obj = await cls.create(poll_id=poll_id, user_id=user_id, **kwargs)
        else:
            await obj.update(poll_id=poll_id, user_id=user_id, **kwargs).apply()
        return obj

    _idx = Index('user_poll_id_index', 'id')

    def __str__(self):
        obj = "Время создания : " + str(self.time_created) + "\n"
        obj += "Последнее изменение : " + str(self.time_updated) + "\n"
        return str(obj)


async def create_database():
    await database.set_bind(DATABASE_URL)
    try:
        await database.gino.create_all()
    except InvalidRequestError:
        pass
    finally:
        await Type.init_types()