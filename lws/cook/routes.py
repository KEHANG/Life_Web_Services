from flask_login import login_required
from flask import flash, redirect, url_for, render_template, request

from lws import lws_db
from lws.models import Dish, Ingredient
from lws.cook import bp
from lws.cook.forms import DishForm, IngredientForm

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

@bp.route('/add_dish', methods=['GET', 'POST'])
@login_required
def add_dish():
    page = request.args.get('page', 1, type=int)
    dishes = Dish.query.paginate(page, 25, False)

    next_url = None
    if dishes.has_next:
        next_url = url_for('cook.add_dish', page=dishes.next_num)
    prev_url = None
    if dishes.has_prev:
        prev_url = url_for('cook.add_dish', page=dishes.prev_num)

    form = DishForm()
    if form.validate_on_submit():
        if form.add_entry.data:
            form.ingredients.append_entry()
            return render_template('cook/add_dish.html', 
                                    title='Dish', 
                                    form=form,
                                    dishes=dishes.items,
                                    next_url=next_url,
                                    prev_url=prev_url)
        elif form.submit.data:
            dish = Dish(name=form.dish_name.data)            
            lws_db.session.add(dish)

            for ingredient_name in form.ingredients.data:
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                if ingredient is None:
                    ingredient = Ingredient(name=ingredient_name)            
                    lws_db.session.add(ingredient)
                dish.add_ingredient(ingredient)

            lws_db.session.commit()
            flash('New dish is added.')
            return redirect(url_for('cook.add_dish'))

    return render_template('cook/add_dish.html', 
                            title='Dish', 
                            form=form,
                            dishes=dishes.items,
                            next_url=next_url,
                            prev_url=prev_url)