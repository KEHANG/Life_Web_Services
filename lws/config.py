import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env_vars'))

class Config(object):
    
    SECRET_KEY = os.environ.get('LWS_SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('LWS_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lws_db.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMIN')]

    POSTS_PER_PAGE = 25
    LANGUAGES = ['en', 'zh']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    STOCK_DB_CONNECTION_STR = os.environ.get('STOCK_DB_CONNECTION_STR')