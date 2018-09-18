from lws import lws_db

class User(lws_db.Model):
    id = lws_db.Column(lws_db.Integer, primary_key=True)
    username = lws_db.Column(lws_db.String(64), index=True, unique=True)
    email = lws_db.Column(lws_db.String(120), index=True, unique=True)
    password_hash = lws_db.Column(lws_db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)