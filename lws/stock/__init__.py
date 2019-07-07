from flask import Blueprint

bp = Blueprint('stock', __name__)

from lws.stock import routes