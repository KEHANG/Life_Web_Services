from flask import Flask
from lws.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

lws_app = Flask(__name__)
lws_app.config.from_object(Config)
lws_db = SQLAlchemy(lws_app)
migrate = Migrate(lws_app, lws_db)

from lws import routes, models