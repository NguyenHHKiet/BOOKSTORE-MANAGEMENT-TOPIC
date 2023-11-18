from flask import render_template, request, Blueprint, url_for, redirect, flash
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore.users.forms import UpdateAccountForm
from bookstore.users.utils import save_picture
from bookstore import db

users = Blueprint('users', __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html", title='Register')

@users.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", title='Login')

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