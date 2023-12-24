import datetime

from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore.models import Order, Book, OrderDetails, User
from bookstore.orders.forms import Checkout
from bookstore.cart.utils import handle_cart
from bookstore import  dao, utils


orders = Blueprint('orders', __name__)

@orders.route("/orders")
def orderBooks():
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login", next=request.url))
    orders = dao.get_orders_by_customer_id(current_user.id)
    return render_template('orderBooks.html', title='Order Books', orders=orders, datetime=datetime.datetime)

@orders.route('/checkout', methods=['GET', 'POST'])
def checkout():
    configuration = dao.get_configuration()
    payment_methods = dao.get_payment_method_all()
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login", next=request.url))

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    form = Checkout()
    form.payment_type.choices = [(method.id, method.name) for method in payment_methods]
    if request.method == "GET":
        form.full_name.data = current_user.first_name + " " + current_user.last_name
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
        form.address.data = current_user.address

    elif form.validate_on_submit():
        # staff is the one who managed online order, has id = 2
        order = utils.create_order(current_user.id, 2, session['cart'], form.payment_type.data)
        session['cart'] = []
        session.modified = True

        if current_user.phone_number != form.phone_number.data or current_user.address != form.address.data:
            update_user = dao.get_user_by_id(current_user.id)
            update_user.phone_number = form.phone_number.data
            update_user.address = form.address.data
            dao.save_user(update_user)
        return redirect(url_for('orders.orderBooks'))
    return render_template('checkout.html', form=form, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total, quick_ship=configuration.quick_ship)
