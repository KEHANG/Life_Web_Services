from flask import Blueprint

bp = Blueprint('lightcom', __name__)

from lws.lightcom import routes