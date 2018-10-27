from flask import Blueprint

bp = Blueprint('cook', __name__)

from lws.cook import routes