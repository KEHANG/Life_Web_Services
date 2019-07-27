import os
import pymongo
from pymongo import MongoClient
from flask_login import login_required
from flask import (current_app, flash, jsonify,
                  redirect, render_template, url_for)

from lws import lws_db
from lws.stock import bp
from lws.models import StockShare
from lws.stock.forms import StockShareForm

def connect_to_record_db():
    db_connection_str = os.environ.get('DB_CONNECTION_STR')
    
    return MongoClient(db_connection_str)

def query_stats(stock_id):

    db_client = MongoClient(current_app.config['STOCK_DB_CONNECTION_STR'])
    db = db_client.lws
    collection = db.stock
    if stock_id.lower() == 'all':
        results = []
        stock_list = ['MSFT', 'SPY', 
                      'AAPL', 'NVDA', 'GOOGL', 'AMZN', 
                      'TWLO', 'BAND', 'TEAM', 'OKTA', 
                      'KO', 'BRK.B']
        for stock in stock_list:
            query = {'stock': stock}
            result = collection.find_one(query, sort=[("updated_utctime", 
                                                       pymongo.DESCENDING)])
            result.pop('_id', None)
            results.append(result)
        
        return results
    else:
        query = {'stock': stock_id.upper()}
        result = collection.find_one(query, sort=[("updated_utctime", 
                                                   pymongo.DESCENDING)])
        result.pop('_id', None)
        return result

@bp.route('/<stock_id>', methods=['GET'])
@login_required
def view_stats(stock_id):

    stats = query_stats(stock_id)
    return render_template('stock/stock_base.html',
                           title='Stock',
                           stats=stats)


@bp.route('/print_stats/<stock_id>', methods=['GET'])
@login_required
def print_stats(stock_id):
    stats = query_stats(stock_id)
    return jsonify(stats)

@bp.route('/activity_register', methods=['GET', 'POST'])
@login_required
def activity_register():
    form = StockShareForm()
    if form.validate_on_submit():
      if form.action.data == 'buy':
        for _ in range(form.shares.data):
          share = StockShare(name=form.stock_name.data,
                             buy_price=form.price.data,
                             buy_timestamp=form.date.data)
          lws_db.session.add(share)
      elif form.action.data == 'sell':
        for _ in range(form.shares.data):
          share = StockShare(name=form.stock_name.data,
                             sell_price=form.price.data,
                             sell_timestamp=form.date.data)
          lws_db.session.add(share)

      lws_db.session.commit()
      flash("Congratulations, you've registered {0} shares of {1}!".format(
            form.shares.data, form.stock_name.data))
      return redirect(url_for('stock.activity_register'))
    return render_template('stock/activity_register.html', title='Stock Activity Register', form=form)