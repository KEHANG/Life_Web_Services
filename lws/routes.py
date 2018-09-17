from lws import lws_app

@lws_app.route('/')
@lws_app.route('/index')
def index():
    return "Hello, Welcome to Life Web Service."