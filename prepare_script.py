from image_format_script import image_convert_script
from data.db_session import global_init, create_session
from data.user import User
from data.post import Post
from data.status import Status

global_init('./db/database.sqlite3')


def create_statuses():
    s = create_session()
    api  = Status(
        name='API user',
        id=0
    )
    s.add(api)
    admin = Status(
        name='admin',
        id=1
    )
    s.add(admin)
    user = Status(
        name='user',
        id=2
    )
    s.add(user)
    s.commit()


def create_users():
    s = create_session()
    user = User(
        nickname='admin',
        status_id=1,
    )
    user.set_password('admin')
    s.add(user)

    for i in range(1, 11):
        nick = f'user{i}'
        user = User(
            nickname=nick,
            status_id=2,
        )
        user.set_password(nick)
        s.add(user)
    
    s.commit()


def create_posts():
    s = create_session()
    for i in range(1, 11):
        nick = f'user{i}'
        user = s.query(User).filter(User.nickname == nick).first()
        image_convert_script(f'{i}.jpg')
        post = Post(
            description=f'Этой мой 1 пост )',
            media=f'{i}.jpg',
            author_id=user.id,
        )
        s.add(post)
        image_convert_script(f'{i + 10}.jpg')
        post = Post(
            description=f'Этой мой 2 пост )',
            media=f'{i + 10}.jpg',
            author_id=user.id,
        )
        s.add(post)
    s.commit()


def preparation():
    create_statuses()
    create_users()
    create_posts()


if __name__ == '__main__':
    preparation()
