import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from app import app, flask_bcrypt, db
from app.forms import RegistrationForms, LoginForms, AccountForms, PostForm
from app.models import User, Post


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForms()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and flask_bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('itinerary'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Log In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForms()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        registered_user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(registered_user)
        db.session.commit()
        flash('User account successfully created', 'success')
        return redirect(url_for('itinerary'))
    return render_template('register.html', title='Register', form=form)


@app.route('/itinerary')
@login_required
def itinerary():
    posts = Post.query.all()
    return render_template('itinerary.html', title='Itinerary', posts=posts)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForms()
    if form.validate_on_submit():
        if form.change_password.data:
            current_user.password_hash = flask_bcrypt.generate_password_hash(form.change_password.data).decode('utf-8')
        if form.user_image.data:
            picture_file = save_picture(form.user_image.data)
            current_user.user_image = picture_file
        db.session.commit()
        return redirect(url_for('account'))
    user_image = url_for('static', filename='profile_pics/' + current_user.user_image)
    return render_template('account.html', title='Account', user_image=user_image, form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('itinerary'))
    return render_template('create_post.html', title='New Post', form=form, legend='Nova objava')


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update post')


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('itinerary'))
