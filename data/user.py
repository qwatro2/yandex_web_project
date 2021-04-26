import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id =  Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False, unique=True)
    status_id = Column(Integer, ForeignKey('statuses.id'))
    status = orm.relation('Status')
    created_date = Column(DateTime, default=datetime.datetime.now)

    def set_password(self, password) -> None:
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password) -> bool:
        return check_password_hash(self.hashed_password, password)
    