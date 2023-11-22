from flask import render_template, request, Blueprint, url_for, redirect, flash
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore.users.forms import UpdateAccountForm, RegistrationForm, LoginForm
from bookstore.users.utils import save_picture
from bookstore.models import User
from bookstore import db, user_datastore
from flask_security.utils import hash_password, verify_password, login_user

users = Blueprint('users', __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.get_user()
        print("Register User: %s" % user)
        if not user:
            hashed_password = hash_password(form.password.data)
            user_datastore.create_user(
                username=form.username.data, email=form.email.data, password=hashed_password
            )
            db.session.commit()
            flash(f"Your account has been created! You're now able to login {form.username.data}!", "success")
            return redirect(url_for('users.login'))
    return render_template("register.html", title='Registration', form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        print("Login User: %s" % user)
        if user:
            login_user(user, remember=form.remember.data)
            flash(f'You have been logged in!', 'success')
            # remember previous page is required and transferred to login
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title='Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        if current_user.username != form.username.data or form.picture.data:
            current_user.username = form.username.data
            db.session.commit()
            flash("Your account has been updated!", "success")
            return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title='Account',image_file=image_file, form=form)

# Decorator which specifies that a user must have at least one of the specified roles.
@users.route('/staff', methods=["GET", "POST"])
@roles_accepted('staff', 'admin')
def staff():
    return render_template("staff.html", title='Staff')