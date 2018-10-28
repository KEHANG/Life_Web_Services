import jwt
from time import time
from hashlib import md5
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from lws import login
from lws import lws_db
from lws.search import add_to_index, remove_from_index, query_index

followers = lws_db.Table('followers',
    lws_db.Column('follower_id', lws_db.Integer, lws_db.ForeignKey('user.id')),
    lws_db.Column('followed_id', lws_db.Integer, lws_db.ForeignKey('user.id'))
)

ingredients = lws_db.Table('ingredients',
    lws_db.Column('dish_id', lws_db.Integer, lws_db.ForeignKey('dish.id')),
    lws_db.Column('ingredient_id', lws_db.Integer, lws_db.ForeignKey('ingredient.id'))
)

menus = lws_db.Table('menus',
    lws_db.Column('menu_id', lws_db.Integer, lws_db.ForeignKey('menu.id')),
    lws_db.Column('dish_id', lws_db.Integer, lws_db.ForeignKey('dish.id'))
)

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            lws_db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

lws_db.event.listen(lws_db.session, 'before_commit', SearchableMixin.before_commit)
lws_db.event.listen(lws_db.session, 'after_commit', SearchableMixin.after_commit)

class User(UserMixin, lws_db.Model):
    id = lws_db.Column(lws_db.Integer, primary_key=True)
    username = lws_db.Column(lws_db.String(64), index=True, unique=True)
    email = lws_db.Column(lws_db.String(120), index=True, unique=True)
    password_hash = lws_db.Column(lws_db.String(128))
    posts = lws_db.relationship('Post', backref='author', lazy='dynamic')

    about_me = lws_db.Column(lws_db.String(140))
    last_seen = lws_db.Column(lws_db.DateTime, default=datetime.utcnow)

    followed = lws_db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=lws_db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(SearchableMixin, lws_db.Model):
    __searchable__ = ['body']

    id = lws_db.Column(lws_db.Integer, primary_key=True)
    body = lws_db.Column(lws_db.String(140))
    timestamp = lws_db.Column(lws_db.DateTime, index=True, default=datetime.utcnow)
    user_id = lws_db.Column(lws_db.Integer, lws_db.ForeignKey('user.id'))
    language = lws_db.Column(lws_db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Menu(lws_db.Model):

    id = lws_db.Column(lws_db.Integer, primary_key=True)
    timestamp = lws_db.Column(lws_db.DateTime, index=True, default=datetime.utcnow)
    confirmed = lws_db.Column(lws_db.Boolean, default=False)
    dishes = lws_db.relationship('Dish', secondary=menus, lazy='dynamic',
                                 backref=lws_db.backref('menus', lazy='dynamic'))

    def __repr__(self):
        return '<Menu {}>'.format(self.name)

    def add_dish(self, dish):
        if not self.has_dish(dish):
            self.dishes.append(dish)

    def remove_dish(self, dish):
        if self.has_dish(dish):
            self.dishes.remove(dish)

    def has_dish(self, dish):
        return self.dishes.filter(
            menus.c.dish_id == dish.id).count() > 0

class Dish(lws_db.Model):

    id = lws_db.Column(lws_db.Integer, primary_key=True)
    name = lws_db.Column(lws_db.String(140))
    ingredients = lws_db.relationship('Ingredient', secondary=ingredients, lazy='dynamic',
                                      backref=lws_db.backref('dishes', lazy='dynamic'))

    def __repr__(self):
        return '<Dish {}>'.format(self.name)

    def add_ingredient(self, ingredient):
        if not self.has_ingredient(ingredient):
            self.ingredients.append(ingredient)

    def remove_ingredient(self, ingredient):
        if self.has_ingredient(ingredient):
            self.ingredients.remove(ingredient)

    def has_ingredient(self, ingredient):
        return self.ingredients.filter(
            ingredients.c.ingredient_id == ingredient.id).count() > 0

class Ingredient(lws_db.Model):

    id = lws_db.Column(lws_db.Integer, primary_key=True)
    name = lws_db.Column(lws_db.String(140))

    def __repr__(self):
        return '<Ingredient {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))



