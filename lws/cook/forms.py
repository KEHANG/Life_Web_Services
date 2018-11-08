from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import DataRequired, ValidationError

from lws.models import Menu, Dish, Ingredient

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

class MenuForm(FlaskForm):
    menu_name = StringField('Menu', validators=[DataRequired()])
    dishes = FieldList(StringField('Dish', validators=[DataRequired()]), min_entries=1)
    add_entry = SubmitField('One more dish')
    pop_entry = SubmitField('remove last dish')
    submit = SubmitField('Submit')

    def __init__(self, original_menu_name, *args, **kwargs):
        super(MenuForm, self).__init__(*args, **kwargs)
        self.original_menu_name = original_menu_name

    def validate_menu_name(self, menu_name):
        if menu_name.data != self.original_menu_name:
            menu = Menu.query.filter_by(name=menu_name.data).first()
            if menu is not None:
                raise ValidationError('{0} is already in the system.'.format(menu_name.data))