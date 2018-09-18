import os

class Config(object):
    
    SECRET_KEY = os.environ.get('LWS_SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('LWS_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False