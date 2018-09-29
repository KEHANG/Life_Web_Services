from flask import render_template
from lws import lws_db
from lws.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    lws_db.session.rollback()
    return render_template('errors/500.html'), 500