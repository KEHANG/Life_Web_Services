import os

class Config(object):
    
    SECRET_KEY = os.environ.get('LWS_SECRET_KEY')