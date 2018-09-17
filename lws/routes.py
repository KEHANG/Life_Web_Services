from flask import render_template

from lws import lws_app
from lws.forms import LoginForm

@lws_app.route('/')
@lws_app.route('/index')
def index():
    user = {'username': 'Kehang'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@lws_app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)