from sqlalchemy import Column, Integer, String, orm
from .db_session import SqlAlchemyBase


class Status(SqlAlchemyBase):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    users = orm.relation('User', back_populates='status')