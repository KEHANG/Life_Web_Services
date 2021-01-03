from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (SelectField, StringField, IntegerField, 
					 SubmitField, DateField, DecimalField)

class StockShareForm(FlaskForm):
    stock_name = StringField('Stock', validators=[DataRequired()])
    action = SelectField('Action',
    					 choices=[('buy', 'buy'), ('sell', 'sell'), ('split', 'split')],
    					 validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    price =  DecimalField('Price', validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired()])
    split_ratio = IntegerField('Split Ratio', validators=[DataRequired()])
    submit = SubmitField('Submit')