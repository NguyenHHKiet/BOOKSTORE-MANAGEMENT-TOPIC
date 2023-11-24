from flask import Blueprint,render_template, redirect, url_for, flash
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore import Book

orders = Blueprint('orders', __name__)

@orders.route("/orders")
def orderBooks():
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login"))
    return render_template('orderBooks.html', title='Order Books')
