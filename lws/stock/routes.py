import os
import pymongo
from datetime import datetime
from sqlalchemy import extract
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

def query_price_stats(stock_id):

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

    stats = query_price_stats(stock_id)
    return render_template('stock/stock_base.html',
                           title='Stock',
                           stats=stats)


@bp.route('/print_stats/<stock_id>', methods=['GET'])
@login_required
def print_stats(stock_id):
    stats = query_price_stats(stock_id)
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
        lws_db.session.commit()
        flash("Congratulations, you've registered {0} shares of {1}!".format(
              form.shares.data, form.stock_name.data))
      
      elif form.action.data == 'sell':
        shares_held = StockShare.query.filter_by(
                              name=form.stock_name.data,
                              sell_price=None
                              ).count()
        if form.shares.data > shares_held:
          flash("Error, only held {0} shares of {1} but you're selling {2}!".format(
              shares_held, form.stock_name.data, form.shares.data))
        elif form.shares.data > 0:
          shares_to_sell = StockShare.query.filter_by(
                              name=form.stock_name.data,
                              sell_price=None
                              ).order_by(StockShare.buy_timestamp).limit(form.shares.data).all()
          for share in shares_to_sell:
            share.sell_price = form.price.data
            share.sell_timestamp = form.date.data
          lws_db.session.commit()
          flash("Congratulations, you've sold {0} shares of {1}!".format(
              form.shares.data, form.stock_name.data))
      elif form.action.data == 'split':
        shares_to_split = StockShare.query.filter_by(
                            name=form.stock_name.data,
                            sell_price=None
                            ).order_by(StockShare.buy_timestamp).all()
        num_shares_split = 0
        for share in shares_to_split:
          if share.buy_timestamp >= datetime.combine(form.date.data, datetime.min.time()):
            break
          share.sell_price = form.price.data
          share.sell_timestamp = form.date.data
          num_shares_split += 1

        for _ in range(num_shares_split*form.split_ratio.data):
          share = StockShare(name=form.stock_name.data,
                             buy_price=form.price.data/form.split_ratio.data,
                             buy_timestamp=form.date.data)
          lws_db.session.add(share)
        lws_db.session.commit()
        flash("Congratulations, you've splitted {0} shares of {1} with split ratio {2}!".format(
              form.shares.data, form.stock_name.data, form.split_ratio.data))

      return redirect(url_for('stock.activity_register'))
    return render_template('stock/activity_register.html', title='Stock Activity Register', form=form)

@bp.route('/monthly_view/<int:year>/<int:month>', methods=['GET'])
@login_required
def monthly_view(year, month):

  stocks_bought = StockShare.query.filter(
                      extract('year', StockShare.buy_timestamp) == year
                    ).filter(
                        extract('month', StockShare.buy_timestamp) == month
                      ).all()

  invest_amount = 0
  exit_amount = 0
  stayed_amount = 0
  latest_price_dict = {}
  stock_bought_overview = {}
  for stock in stocks_bought:
    invest_amount += stock.buy_price
    if stock.name not in stock_bought_overview:
      stock_bought_overview[stock.name] = 1
    else:
      stock_bought_overview[stock.name] += 1
    # we also sold this stock share already
    # between that month and now
    if stock.sell_price:
      exit_amount += stock.sell_price
    else:
      if stock.name not in latest_price_dict:
        stock_info = query_price_stats(stock.name)
        latest_price = stock_info['last_5day_prices'][-1]
        latest_price_dict[stock.name] = latest_price
      else:
        latest_price = latest_price_dict[stock.name]
      stayed_amount += latest_price

  # calculate return of investment
  now = datetime.utcnow()
  month_diff = 12 * (now.year - year) + (now.month - month)
  money_overview = {
          'invest_amount': invest_amount,
          'exit_amount': exit_amount,
          'stayed_amount': stayed_amount}
  if month_diff == 0 or invest_amount == 0:
    money_overview['yearly_roi'] = 'NA'
    money_overview['yearly_gain'] = 'NA'
  else:
    yearly_roi = (((stayed_amount + exit_amount) / invest_amount)**(12.0/month_diff) - 1)
    money_overview['yearly_roi'] = '{0}%'.format(yearly_roi * 100)
    money_overview['yearly_gain'] = invest_amount * yearly_roi
  
  return jsonify({'money_overview': money_overview,
                  'stock_bought_overview': stock_bought_overview})

@bp.route('/holding_view', methods=['GET'])
@login_required
def holding_view():

    stocks_held = StockShare.query.filter_by(sell_price=None).all()
    holding_dict = {}
    for stock in stocks_held:
      if stock.name not in holding_dict:
        holding_dict[stock.name] = 1
      else:
        holding_dict[stock.name] += 1

    return jsonify(holding_dict)
