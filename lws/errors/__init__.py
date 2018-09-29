from flask import Blueprint

bp = Blueprint('errors', __name__)

from lws.errors import handlers