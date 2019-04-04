import os
from flask_login import login_required
from flask import render_template, flash, redirect, url_for

from lws.lightcom import bp
from lws.lightcom.publish import publish_msg

consumers = os.environ.get('MQ_CONSUMERS').split(':')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def main():

    return render_template('lightcom/lightcom.html', 
                            title='Lightcom')

@bp.route('/at_home', methods=['GET'])
@login_required
def at_home():
    for consumer in consumers:
        publish_msg('turn_on_green', 'MQ_{0}'.format(consumer))
        publish_msg('turn_off_red', 'MQ_{0}'.format(consumer))
        publish_msg('turn_off_blue', 'MQ_{0}'.format(consumer))
    flash('At-Home Message is published.')
    return redirect(url_for('lightcom.main'))

@bp.route('/at_work', methods=['GET'])
@login_required
def at_work():
    for consumer in consumers:
        publish_msg('turn_on_red', 'MQ_{0}'.format(consumer))
        publish_msg('turn_off_green', 'MQ_{0}'.format(consumer))
        publish_msg('turn_off_blue', 'MQ_{0}'.format(consumer))
    flash('At-Work Message is published.')
    return redirect(url_for('lightcom.main'))

@bp.route('/on_the_way', methods=['GET'])
@login_required
def on_the_way():
    for consumer in consumers:
        publish_msg('turn_off_red', 'MQ_{0}'.format(consumer))
        publish_msg('turn_off_green', 'MQ_{0}'.format(consumer))
        publish_msg('turn_on_blue', 'MQ_{0}'.format(consumer))
    flash('On-The-Way Message is published.')
    return redirect(url_for('lightcom.main'))