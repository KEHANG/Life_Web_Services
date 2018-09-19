from datetime import datetime

from lws import lws_db

class User(lws_db.Model):
    id = lws_db.Column(lws_db.Integer, primary_key=True)
    username = lws_db.Column(lws_db.String(64), index=True, unique=True)
    email = lws_db.Column(lws_db.String(120), index=True, unique=True)
    password_hash = lws_db.Column(lws_db.String(128))
    posts = lws_db.relationship('Post', backref='author', lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(lws_db.Model):
    id = lws_db.Column(lws_db.Integer, primary_key=True)
    body = lws_db.Column(lws_db.String(140))
    timestamp = lws_db.Column(lws_db.DateTime, index=True, default=datetime.utcnow)
    user_id = lws_db.Column(lws_db.Integer, lws_db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)