from flask import Blueprint

bp = Blueprint('auth', __name__)

from lws.auth import routes