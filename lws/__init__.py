import os
import logging
from flask import Flask
from flask_mail import Mail
from lws.config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import SMTPHandler, RotatingFileHandler

lws_app = Flask(__name__)
lws_app.config.from_object(Config)

lws_db = SQLAlchemy(lws_app)
migrate = Migrate(lws_app, lws_db)

login = LoginManager(lws_app)
login.login_view = 'login'
mail = Mail(lws_app)


from lws import routes, models, errors

if not lws_app.debug:
    if lws_app.config['MAIL_SERVER']:
        auth = None
        if lws_app.config['MAIL_USERNAME'] or lws_app.config['MAIL_PASSWORD']:
            auth = (lws_app.config['MAIL_USERNAME'], lws_app.config['MAIL_PASSWORD'])
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
