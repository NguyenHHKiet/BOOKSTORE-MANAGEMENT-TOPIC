from flask import render_template, request, Blueprint, url_for, redirect
from flask_security import logout_user, current_user

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
def account():
    if not current_user.is_authenticated:
        return render_template("login.html")
    return render_template("account.html", title='Account')
