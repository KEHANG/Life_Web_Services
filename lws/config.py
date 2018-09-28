import os

class Config(object):
    
    SECRET_KEY = os.environ.get('LWS_SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('LWS_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['kehanghan@gmail.com']

    POSTS_PER_PAGE = 25

    LANGUAGES = ['en', 'zh']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')