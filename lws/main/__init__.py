from flask import Blueprint

bp = Blueprint('main', __name__)

from lws.main import routes