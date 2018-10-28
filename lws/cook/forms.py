from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import DataRequired, ValidationError

from lws.models import Dish, Ingredient

class IngredientForm(FlaskForm):
    ingredient_name = StringField('Ingredient', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ingredient_name(self, ingredient_name):
        ingredient = Ingredient.query.filter_by(name=ingredient_name.data).first()
        if ingredient is not None:
            raise ValidationError('{0} is already in the system.'.format(ingredient_name.data))

class DishForm(FlaskForm):
    dish_name = StringField('Dish', validators=[DataRequired()])
    ingredients = FieldList(StringField('Ingredient', validators=[DataRequired()]), min_entries=1)
    add_entry = SubmitField('One more ingredient')
    submit = SubmitField('Submit')

    def validate_dish_name(self, dish_name):
        dish = Dish.query.filter_by(name=dish_name.data).first()
        if dish is not None:
            raise ValidationError('{0} is already in the system.'.format(dish_name.data))