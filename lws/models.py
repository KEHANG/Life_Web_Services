from hashlib import md5
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from lws import login
from lws import lws_db

followers = lws_db.Table('followers',
    lws_db.Column('follower_id', lws_db.Integer, lws_db.ForeignKey('user.id')),
    lws_db.Column('followed_id', lws_db.Integer, lws_db.ForeignKey('user.id'))
)

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



class Post(lws_db.Model):
    id = lws_db.Column(lws_db.Integer, primary_key=True)
    body = lws_db.Column(lws_db.String(140))
    timestamp = lws_db.Column(lws_db.DateTime, index=True, default=datetime.utcnow)
    user_id = lws_db.Column(lws_db.Integer, lws_db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))



