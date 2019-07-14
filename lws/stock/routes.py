import os
import pymongo
from pymongo import MongoClient
from flask_login import login_required
from flask import current_app, jsonify, render_template

from lws.stock import bp

def connect_to_record_db():
    db_connection_str = os.environ.get('DB_CONNECTION_STR')
    
    return MongoClient(db_connection_str)

@bp.route('/<stock_id>', methods=['GET'])
@login_required
def view_stats(stock_id):

  return render_template('stock/stock_base.html', 
                         title='Stock')


@bp.route('/latest_stats/<stock_id>', methods=['GET'])
@login_required
def latest_stats(stock_id):
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
        
        return jsonify(results)
    else:
        query = {'stock': stock_id.upper()}
        result = collection.find_one(query, sort=[("updated_utctime", 
                                                   pymongo.DESCENDING)])
        result.pop('_id', None)
        return jsonify(result)