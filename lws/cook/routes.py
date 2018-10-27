from flask_login import login_required
from flask import flash, redirect, url_for, render_template, request

from lws import lws_db
from lws.models import Ingredient
from lws.cook import bp
from lws.cook.forms import IngredientForm

@bp.route('/add_ingredient', methods=['GET', 'POST'])
@login_required
def add_ingredient():
    form = IngredientForm()
    if form.validate_on_submit():
        ingredient = Ingredient(name=form.ingredient_name.data)
        lws_db.session.add(ingredient)
        lws_db.session.commit()
        flash('New ingredient is added.')
        return redirect(url_for('cook.add_ingredient'))

    page = request.args.get('page', 1, type=int)
    ingredients = Ingredient.query.paginate(page, 25, False)

    next_url = None
    if ingredients.has_next:
        next_url = url_for('cook.add_ingredient', page=ingredients.next_num)
    prev_url = None
    if ingredients.has_prev:
        prev_url = url_for('cook.add_ingredient', page=ingredients.prev_num)

    return render_template('cook/add_ingredient.html', 
                            title='Ingredient', 
                            form=form,
                            ingredients=ingredients.items,
                            next_url=next_url,
                            prev_url=prev_url)