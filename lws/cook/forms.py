from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from lws.models import Ingredient

class IngredientForm(FlaskForm):
    ingredient_name = StringField('Ingredient', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ingredient_name(self, ingredient_name):
        user = Ingredient.query.filter_by(name=ingredient_name.data).first()
        if user is not None:
            raise ValidationError('{0} is already in the system.'.format(ingredient_name.data))