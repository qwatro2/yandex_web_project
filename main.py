from resources import PostListResource, PostResource, UserListResource, UserResource
from flask_login import current_user
from werkzeug.utils import secure_filename
from forms.newpostform import NewPostForm
from flask import abort
from data.post import Post
from sqlalchemy import desc
from flask_login.utils import login_user, logout_user
from forms.registerform import RegisterForm
from flask.templating import render_template
from forms.loginform import LoginForm
from flask import Flask, redirect
from flask_login import LoginManager
from data import db_session
from data.user import User
from image_format_script import image_convert_script
from flask_restful import Api


def page_not_found(e):
    return render_template('404.html'), 404


def server_error(e):
    return render_template('500.html'), 500


app = Flask(__name__)
app.config['SECRET_KEY'] = 'EGOR SHIP CRASH'
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, server_error)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).order_by(desc(Post.create_date)).all()
    if not current_user.is_authenticated:
        posts = posts[:30]
    return render_template('index.html', posts=posts)


@app.route('/@<nickname>')
def user_page(nickname):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        author = db_sess.query(User).filter(User.nickname == nickname).first()
        if author:
            posts = db_sess.query(Post).filter(Post.author == author)\
                    .order_by(desc(Post.create_date)).all()
            return render_template('user_page.html', nickname=nickname, posts=posts)
        else:
            abort(404)
    else:
        return render_template('unauthenticated.html')


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if current_user.is_authenticated:
        form = NewPostForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            post = Post()
            post.description = form.description.data
            f = form.media.data
            filename = secure_filename(f.filename)
            f.save(f'./static/media/{filename}')
            image_convert_script(filename)
            post.media = filename
            post.author_id = current_user.id
            db_sess.add(post)
            db_sess.commit()
            return redirect('/')
        return render_template('new_post.html', form=form)
    else:
        return render_template('unauthenticated.html')


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect("/")
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
        return render_template('login.html', message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if ' ' in form.nickname.data:
            return render_template('register.html',
                                   message='Никнейм не должен содержать пробелы',
                                   form=form)
        if form.password.data != form.password_again.data:
            return render_template('register.html', message='Пароли не совпадают',
                                   form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', message='Никнейм занят',
                                   form=form)
        user = User()
        user.nickname = form.nickname.data
        user.status_id = 2
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


if __name__ == '__main__':
    db_session.global_init("db/database.sqlite3")
    api.add_resource(PostListResource, '/api/posts')
    api.add_resource(PostResource, '/api/post/<int:post_id>')
    api.add_resource(UserListResource, '/api/users')
    api.add_resource(UserResource, '/api/user/<int:user_id>')
    app.run(port=8080, host='127.0.0.1')
