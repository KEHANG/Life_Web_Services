from flask import Flask
from lws.config import Config

lws_app = Flask(__name__)
lws_app.config.from_object(Config)

from lws import routes