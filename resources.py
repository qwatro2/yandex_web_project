from flask_restful import reqparse, abort, Resource
from data import db_session
from data.post import Post
from flask import jsonify
from data.user import User
import base64


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    if not post:
        abort(404, message=f"Post {post_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('description', required=True, type=str)
parser.add_argument('media', required=True, type=str)


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        data = post.to_dict()
        with open(f'./static/media/{data["media"]}', 'rb') as f:
            string = base64.b64encode(f.read()).decode("utf-8")
            data['media'] = string
        return jsonify({'post': data})

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict() for item in posts]})
    
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Post()
        post.description = args['description']
        author = session.query(User).filter(User.status_id == 0).first()
        post.author_id = author.id
        post.media = args['media']
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})


parser1 = reqparse.RequestParser()
parser1.add_argument('nickname', required=True, type=str)
parser1.add_argument('password', required=True, type=str)
parser1.add_argument('status_id', required=True, type=int)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def user_to_dict(user: User):
    session = db_session.create_session()
    posts = session.query(Post).filter(Post.author == user).all()
    p = [post.id for post in posts]
    return {
            'id': user.id,
            'nickname': user.nickname,
            'status_id': user.status_id,
            'created_date': user.created_date,
            'posts_id': p,
        }


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        posts = session.query(Post).filter(Post.author == user).all()
        return jsonify({'user': user_to_dict(user)})
    
    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user_to_dict(user) for user in users]})

    def post(self):
        session = db_session.create_session()
        args = parser1.parse_args()
        user = User(
            nickname=args['nickname'],
            status_id=args['status_id']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
