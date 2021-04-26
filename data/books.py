import sqlalchemy
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    """Класс отвечающиц за внос книги в БД"""
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    language = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pages = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
