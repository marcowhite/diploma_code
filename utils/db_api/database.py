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
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(64))
    description = Column(String(256))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    _idx = Index('poll_id_index', 'id')


class Question(BaseModel):
    __tablename__ = 'questions'

    id = Column(Integer, Sequence('question_id_seq'), primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'))
    type_id = Column(Integer, ForeignKey('types.id'))
    text = Column(String(256))

    _idx = Index('question_id_index', 'id')


class Type(BaseModel):
    __tablename__ = 'types'

    id = Column(Integer, Sequence('question_id_seq'), primary_key=True)
    text = Column(String(256))

    _idx = Index('type_id_index', 'id')


class Answer(BaseModel):
    __tablename__ = 'answers'

    id = Column(Integer, Sequence('answer_id_seq'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(String(256))

    _idx = Index('answer_id_index', 'id')


class UserAnswer(BaseModel):
    __tablename__ = 'user_answers'

    id = Column(Integer, Sequence('user_answer_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answers.id'))

    _idx = Index('user_answer_id_index', 'id')


class UserPoll(BaseModel):
    __tablename__ = 'user_polls'

    id = Column(Integer, Sequence('user_answer_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    _idx = Index('user_poll_id_index', 'id')


async def create_database():
    await database.set_bind(DATABASE_URL)
    try:
        await database.gino.create_all()
    except InvalidRequestError:
        pass
