from flask_babel import _
from datetime import datetime
from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from lws import lws_app, lws_db
from lws.models import User, Post
from lws.email import send_password_reset_email
from lws.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm

@lws_app.route('/', methods=['GET', 'POST'])
@lws_app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
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

@lws_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@lws_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@lws_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        lws_db.session.add(user)
        lws_db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

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

@lws_app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('login'))
        else:
            flash('Your email is not registered in the system')
    return render_template('reset_password_request.html', 
                           title='Reset Password', form=form)

@lws_app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        lws_db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@lws_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        lws_db.session.commit()

