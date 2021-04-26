import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    media = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    author = orm.relation('User')
    create_date = Column(DateTime, default=datetime.datetime.now)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'media': self.media,
            'author_id': self.author_id,
            'create_date': self.create_date,
        }
        
