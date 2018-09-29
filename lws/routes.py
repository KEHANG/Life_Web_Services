from flask import g
from flask import jsonify
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from lws import lws_app, lws_db
from lws.models import User, Post
from lws.translate import translate
from lws.forms import EditProfileForm, PostForm

@lws_app.route('/', methods=['GET', 'POST'])
@lws_app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        lws_db.session.add(post)
        lws_db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, 
            lws_app.config['POSTS_PER_PAGE'], False)

    next_url = None
    if posts.has_next:
        next_url = url_for('index', page=posts.next_num)
    prev_url = None
    if posts.has_prev:
        prev_url = url_for('index', page=posts.prev_num)

    return render_template('index.html', title='Home', form=form, 
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@lws_app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, 
            lws_app.config['POSTS_PER_PAGE'], False)
    next_url = None
    if posts.has_next:
        next_url = url_for('user', username=user.username, page=posts.next_num)
    prev_url = None
    if posts.has_prev:
        prev_url = url_for('user', username=user.username, page=posts.prev_num)
    return render_template('user.html', user=user, 
                           posts=posts.items, next_url=next_url, prev_url=prev_url)

@lws_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        lws_db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@lws_app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    lws_db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@lws_app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    lws_db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@lws_app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 
            lws_app.config['POSTS_PER_PAGE'], False)
    next_url = None
    if posts.has_next:
        next_url = url_for('explore', page=posts.next_num)
    prev_url = None
    if posts.has_prev:
        prev_url = url_for('explore', page=posts.prev_num)

    return render_template('explore.html', title='Explore', 
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@lws_app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@lws_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        lws_db.session.commit()

    g.locale = str(get_locale())
