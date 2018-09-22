from flask import render_template
from lws import lws_app, lws_db

@lws_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@lws_app.errorhandler(500)
def internal_error(error):
    lws_db.session.rollback()
    return render_template('500.html'), 500