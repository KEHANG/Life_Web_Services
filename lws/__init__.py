import os
import logging
from flask_mail import Mail
from flask_babel import Babel, _
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from flask import Flask, request, current_app
from logging.handlers import SMTPHandler, RotatingFileHandler

from lws.config import Config

lws_db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    lws_app = Flask(__name__)
    lws_app.config.from_object(config_class)

    lws_db.init_app(lws_app)
    migrate.init_app(lws_app, lws_db)
    login.init_app(lws_app)
    mail.init_app(lws_app)
    bootstrap.init_app(lws_app)
    moment.init_app(lws_app)
    babel.init_app(lws_app)

    lws_app.elasticsearch = Elasticsearch([lws_app.config['ELASTICSEARCH_URL']]) \
    if lws_app.config['ELASTICSEARCH_URL'] else None


    # register blueprints
    from lws.main import bp as main_bp
    from lws.errors import bp as errors_bp
    from lws.auth import bp as auth_bp

    lws_app.register_blueprint(main_bp)
    lws_app.register_blueprint(errors_bp)
    lws_app.register_blueprint(auth_bp, url_prefix='/auth')

    if not lws_app.debug and not lws_app.testing:
        if lws_app.config['MAIL_SERVER']:
            auth = None
            if lws_app.config['MAIL_USERNAME'] or lws_app.config['MAIL_PASSWORD']:
                auth = (lws_app.config['MAIL_USERNAME'], 
                        lws_app.config['MAIL_PASSWORD'])
            secure = None
            if lws_app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(lws_app.config['MAIL_SERVER'], lws_app.config['MAIL_PORT']),
                fromaddr='no-reply@' + lws_app.config['MAIL_SERVER'],
                toaddrs=lws_app.config['ADMINS'], subject='Life Web Services Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            lws_app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/lws.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        lws_app.logger.addHandler(file_handler)

        lws_app.logger.setLevel(logging.INFO)
        lws_app.logger.info('Life Web Services startup')

    return lws_app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from lws import models
