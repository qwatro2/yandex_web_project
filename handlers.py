from image_format_script import image_convert_script
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from sqlalchemy.sql.expression import desc
from data.db_session import create_session
from data.user import User
from data.post import Post
import random
import time
from sqlite3 import connect
from keyboards import keyboard_cancel, keyboard_is_login, keyboard_isnt_login


class OrderRegister(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_password = State()
    waiting_for_password_again = State()


class OrderLogin(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_password = State()


class OrderAddPost(StatesGroup):
    waiting_for_description = State()
    waiting_for_photo = State()


def is_loginned(message: types.Message) -> bool:
    tg_id = message['from']['id']
    with connect('./db/database.sqlite3') as con:
        cur = con.cursor()
        query = '''SELECT is_login FROM telegram_users
                 WHERE telegram_id == ?'''
        cur.execute(query, (tg_id,))
        is_login_tuple = cur.fetchone()
    
    if is_login_tuple:
        is_login = is_login_tuple[0]
    else:
        is_login = False
        with connect('./db/database.sqlite3') as con:
            cur = con.cursor()
            query = '''INSERT INTO telegram_users 
                    (telegram_id, is_login) VALUES (?, False)'''
            cur.execute(query, (tg_id,))
    return is_login


async def register_start(message: types.Message) -> None:
    await message.answer('<strong>Введите никнейм</strong>', parse_mode='HTML',
                         reply_markup=keyboard_cancel)
    await OrderRegister.waiting_for_nickname.set()


async def register_nickname(message: types.Message, state: FSMContext) -> None:
    if len(message.text.split()) != 1:
        await message.answer('<strong>Никнейм должен состоять из одного слова.'
                             ' Попробуйте еще раз.</strong>', parse_mode='HTML')
        return

    if create_session().query(User).filter(User.nickname == message.text).first():
        await message.answer('<strong>Никнейм занят.'
                             ' Попробуйте еще раз.</strong>', parse_mode='HTML')
        return
    
    await state.update_data(nickname=message.text)
    await OrderRegister.next()
    await message.answer('<strong>Введите пароль</strong>', parse_mode='HTML')


async def register_password(message: types.Message, state: FSMContext) -> None:
    if len(message.text.split()) != 1:
        await message.answer('<strong>Пароль не должен содержать пробелы.'
                             ' Попробуйте еще раз.</strong>', parse_mode='HTML')
        return
    
    await state.update_data(password=message.text)
    await OrderRegister.next()
    await message.answer('<strong>Введите пароль снова</strong>', parse_mode='HTML')


async def register_password_again(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data['password'] != message.text:
        await message.answer('<strong>Пароли не совпадают.'
                             ' Попробуйте еще раз.</strong>', parse_mode='HTML')
        return

    # создание нового пользователя
    user = User(
        nickname=data['nickname'],
        status_id=2
    )
    user.set_password(data['password'])
    s = create_session()
    s.add(user)
    s.commit()

    await state.finish()
    await message.answer('<strong>Регистрация прошла успешно.</strong>',
                         parse_mode='HTML', reply_markup=keyboard_isnt_login)


def register_handlers_register(dp: Dispatcher) -> None:
    dp.register_message_handler(register_start, commands='register', state='*')
    dp.register_message_handler(register_start, Text(equals='регистрация',
                                                     ignore_case=True), state='*')
    dp.register_message_handler(register_nickname,
                                state=OrderRegister.waiting_for_nickname)
    dp.register_message_handler(register_password,
                                state=OrderRegister.waiting_for_password)
    dp.register_message_handler(register_password_again,
                                state=OrderRegister.waiting_for_password_again)


async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    is_login = is_loginned(message)
    if is_login:
        m = keyboard_is_login
    else:
        m = keyboard_isnt_login

    await message.answer('<strong>Привет!</strong>',
                         parse_mode='HTML', reply_markup=m) 


async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    is_login = is_loginned(message)
    if is_login:
        m = keyboard_is_login
    else:
        m = keyboard_isnt_login

    await message.answer('<strong>Действие отменено</strong>',
                         parse_mode='HTML', reply_markup=m) 


def register_handlers_common(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена",
                                                 ignore_case=True), state="*")


async def login_start(message: types.Message) -> None:
    await message.answer('<strong>Введите никнейм</strong>',
                         parse_mode='HTML', reply_markup=keyboard_cancel)
    await OrderLogin.waiting_for_nickname.set()


async def login_nickname(message: types.Message, state: FSMContext) -> None:
    nickname = message.text
    s = create_session()
    user = s.query(User).filter(User.nickname == nickname).first()
    if not user:
        await message.answer('<strong>Пользователь с таким никнеймом '
                             'не найден. Попробуйте еще раз.</strong>', 
                             parse_mode='HTML')
        return
    
    await state.update_data(nickname=nickname)
    await OrderLogin.next()
    await message.answer('<strong>Введите пароль</strong>', parse_mode='HTML')


async def login_password(message: types.Message, state: FSMContext) -> None:
    password = message.text
    data = await state.get_data()
    nickname = data['nickname']
    user = create_session().query(User).filter(User.nickname == nickname).first()
    if not user.check_password(password):
        await message.answer('<strong>Неправильный пароль.'
                             ' Попробуйте еще раз.</strong>', parse_mode='HTML')
        return
    
    with connect('./db/database.sqlite3') as con:
        cur = con.cursor()
        query = '''UPDATE telegram_users SET is_login = 1,
                 nickname = ? WHERE telegram_id = ?'''
        cur.execute(query, (nickname, message['from']['id']))

    await state.finish()
    await message.answer('<strong>Вход выполнен успешно</strong>',
                         parse_mode='HTML', reply_markup=keyboard_is_login)


def register_handlers_login(dp: Dispatcher) -> None:
    dp.register_message_handler(login_start, commands="login", state="*")
    dp.register_message_handler(login_start, Text(equals="вход",
                                                  ignore_case=True), state="*")
    dp.register_message_handler(login_nickname,
                                state=OrderLogin.waiting_for_nickname)
    dp.register_message_handler(login_password,
                                state=OrderLogin.waiting_for_password) 


async def logout(message: types.Message) -> None:
    tg_id = message['from']['id']

    with connect('./db/database.sqlite3') as con:
        cur = con.cursor()
        query = '''SELECT is_login FROM telegram_users 
                WHERE telegram_id = ?'''
        cur.execute(query, (tg_id,))
        is_login = cur.fetchone()

    if is_login is None:
        is_login = False
        with connect('./db/database.sqlite3') as con:
            cur = con.cursor()
            query = '''INSERT INTO telegram_users 
                    (telegram_id, is_login) VALUES (?, False)'''
            cur.execute(query, (tg_id,))
    else:
        is_login = is_login[0]
    
    if not is_login:
        await message.answer('<strong>Вход не был совершен</strong>',
                             parse_mode='HTML')
        return
    
    with connect('./db/database.sqlite3') as con:
        cur = con.cursor()
        query = 'UPDATE telegram_users SET is_login = 0, nickname = ?'
        cur.execute(query, (None,))

    await message.answer('<strong>Выход выполнен успешно.</strong>',
                         parse_mode='HTML', reply_markup=keyboard_isnt_login)


def register_handler_logout(dp: Dispatcher) -> None:
    dp.register_message_handler(logout, commands="logout", state="*")
    dp.register_message_handler(logout, Text(equals="выход",
                                             ignore_case=True), state="*")


async def random_post(message: types.Message) -> None:
    s = create_session()
    post = random.choice(s.query(Post).all())
    text = f'''<strong><a href="http://127.0.0.1:8080/@{post.author.nickname}">
            {post.author.nickname}</a></strong>\n{post.description}'''
    with open(f'./static/media/{post.media}', 'rb') as f:
        await message.answer_photo(f, caption=text, parse_mode='HTML')


async def newest_posts(message: types.Message) -> None:
    is_login = is_loginned(message)
    
    if not is_login:
        await message.answer('<strong>Чтобы посмотреть новые посты,'
                             ' войдите в аккаунт (/login). Если у вас его'
                             ' еще нет, зарегистрируйтесь (/register)</strong>',
                             parse_mode='HTML')
        return
    s = create_session()
    posts = s.query(Post).order_by(desc(Post.create_date)).limit(5).all()
    for post in posts:
        text = f'<strong><a href="http://127.0.0.1:8080/@{post.author.nickname}">' + \
               f'{post.author.nickname}</a></strong>\n{post.description}'
        with open(f'./static/media/{post.media}', 'rb') as f:
            await message.answer_photo(f, caption=text, parse_mode='HTML')
        time.sleep(1)
            

def register_handlers_send_posts(dp: Dispatcher) -> None:
    dp.register_message_handler(random_post, commands='random_post', state='*')
    dp.register_message_handler(random_post, Text(equals='случайный пост', 
                                                  ignore_case=True), state='*')
    dp.register_message_handler(newest_posts, commands='newest_posts', state='*')
    dp.register_message_handler(newest_posts, Text(equals='новые посты',
                                                   ignore_case=True), state='*')


async def add_post_start(message: types.Message) -> None:
    is_login = is_loginned(message)

    if not is_login:
        await message.answer('<strong>Чтобы выложить пост, войдите в '
                             'аккаунт (/login). Если у вас его еще нет'
                             ', зарегистрируйтесь (/register)</strong>', 
                             parse_mode='HTML')
        return
    
    await message.answer('<strong>Введите описание поста</strong>', 
                         parse_mode='HTML', reply_markup=keyboard_cancel)
    await OrderAddPost.waiting_for_description.set()


async def add_post_description(message: types.Message, state:FSMContext) -> None:
    description = message.text
    await state.update_data(description=description)
    await OrderAddPost.next()
    await message.answer('<strong>Отправьте фото</strong>', parse_mode='HTML')


async def add_post_photo(message: types.Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    data = await state.get_data()
    description = data['description']
    tg_id = message['from']['id']
    with connect('./db/database.sqlite3') as con:
        cur = con.cursor()
        query = '''SELECT posts_added, nickname FROM
                 telegram_users WHERE telegram_id = ?'''
        cur.execute(query, (tg_id,))
        index, nickname = cur.fetchone()
        filename = f'{tg_id}_{index}.jpeg'
        query = '''UPDATE telegram_users SET 
                posts_added = ? WHERE telegram_id = ?'''
        cur.execute(query, (index + 1, tg_id,))
    await photo.download(f'./static/media/{filename}')

    image_convert_script(filename)
    s = create_session()
    author_id = s.query(User).filter(User.nickname == nickname).first().id
    post = Post(
        description=description,
        media=filename,
        author_id=author_id
    )
    s.add(post)
    s.commit()

    await state.finish()
    await message.answer('<strong>Пост добавлен успешно</strong>',
                         parse_mode='HTML', reply_markup=keyboard_is_login)


def register_handler_add_post(dp: Dispatcher) -> None:
    dp.register_message_handler(add_post_start, commands='add_post', state='*')
    dp.register_message_handler(add_post_start, Text(equals='добавить пост',
                                                     ignore_case=True), state='*')
    dp.register_message_handler(add_post_description,
                                state=OrderAddPost.waiting_for_description)
    dp.register_message_handler(add_post_photo, content_types='photo',
                                state=OrderAddPost.waiting_for_photo)
