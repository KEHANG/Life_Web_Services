from lws import cli, create_app, lws_db
from lws.models import User, Post

lws_app = create_app()
cli.register(lws_app)

@lws_app.shell_context_processor
def make_shell_context():
    return {'db': lws_db, 'User': User, 'Post': Post}