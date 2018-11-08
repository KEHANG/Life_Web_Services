from flask import jsonify
from flask_login import login_required
from flask import flash, redirect, url_for, render_template, request

from lws import lws_db
from lws.models import Menu, Dish, Ingredient
from lws.cook import bp
from lws.cook.forms import MenuForm, DishForm, IngredientForm

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
        elif form.pop_entry.data:
            form.ingredients.pop_entry()
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

@bp.route('/add_menu', methods=['GET', 'POST'])
@login_required
def add_menu():
    page = request.args.get('page', 1, type=int)
    menus = Menu.query.paginate(page, 25, False)

    next_url = None
    if menus.has_next:
        next_url = url_for('cook.add_menu', page=menus.next_num)
    prev_url = None
    if menus.has_prev:
        prev_url = url_for('cook.add_menu', page=menus.prev_num)

    form = MenuForm(original_menu_name='')
    if form.validate_on_submit():
        if form.add_entry.data:
            form.dishes.append_entry()
        elif form.pop_entry.data:
            form.dishes.pop_entry()
        elif form.submit.data:
            menu = Menu(name=form.menu_name.data)            
            lws_db.session.add(menu)

            # add dishes that are not included in
            # dish table or menus table
            for dish_name in form.dishes.data:
                dish = Dish.query.filter_by(name=dish_name).first()
                if dish is None:
                    dish = Dish(name=dish_name)            
                    lws_db.session.add(dish)
                menu.add_dish(dish)

            lws_db.session.commit()
            flash('New menu is added.')
            return redirect(url_for('cook.add_menu'))

    return render_template('cook/add_menu.html', 
                            title='Menu', 
                            form=form,
                            menus=menus.items,
                            next_url=next_url,
                            prev_url=prev_url)

@bp.route('/edit_menu/<menu_id>', methods=['GET', 'POST'])
@login_required
def edit_menu(menu_id):
    menu = Menu.query.get(menu_id)
    if menu is None:
        flash('Menu {} not found.'.format(menu_id))
        return redirect(url_for('cook.add_menu'))

    form = MenuForm(original_menu_name=menu.name)
    if form.validate_on_submit():
        if form.add_entry.data:
            form.dishes.append_entry()
        elif form.pop_entry.data:
            form.dishes.pop_entry()
        elif form.submit.data:
            # add dishes that are not included in
            # dish table or menus table
            for dish_name in form.dishes.data:
                dish = Dish.query.filter_by(name=dish_name).first()
                if dish is None:
                    dish = Dish(name=dish_name)            
                    lws_db.session.add(dish)
                menu.add_dish(dish)

            # remove dishes that are removed via the form
            dishes_to_rm = []
            for dish in menu.dishes:
                if dish.name not in form.dishes.data:
                    dishes_to_rm.append(dish)
            for dish in dishes_to_rm:
                menu.remove_dish(dish)

            lws_db.session.commit()
            flash('New menu is modified.')
            return redirect(url_for('cook.add_menu'))
    elif request.method == 'GET':
        form.menu_name.data = menu.name
        form.dishes.pop_entry()
        for dish in menu.dishes:
            form.dishes.append_entry(dish.name)

    return render_template('cook/edit_menu.html', 
                           title='Edit Menu', 
                           form=form)

@bp.route('/ingredients')
@login_required
def ingredients():
    ingredients = Ingredient.query.all()
    ingredient_names = [i.name for i in ingredients]
    return jsonify(ingredient_names)

@bp.route('/dishes')
@login_required
def dishes():
    dishes = Dish.query.all()
    dish_names = [i.name for i in dishes]
    return jsonify(dish_names)

@bp.route('/menus')
@login_required
def menus():
    menus = Menu.query.all()
    menu_names = [i.name for i in menus]
    return jsonify(menu_names)


