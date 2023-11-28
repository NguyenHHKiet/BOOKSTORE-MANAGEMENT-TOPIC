from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore.models import Order, Book, OrderDetails, User
from bookstore.orders.forms import Checkout
from bookstore.cart.utils import handle_cart
from bookstore import db
import random, datetime

orders = Blueprint('orders', __name__)

@orders.route("/orders")
def orderBooks():
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login", next=request.url))
    orders = Order.query.order_by(Order.id.desc())
    print(orders)
    return render_template('orderBooks.html', title='Order Books')

@orders.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login", next=request.url))
    
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    if form.validate_on_submit():
        print(form.first_name.data, form.last_name.data, form.email.data, form.phone_number.data)
        print(form.address.data, form.city.data, form.country.data)
        print(form.payment_type.data)
        order = Order()
        end_date = datetime.date.today() + datetime.timedelta(days=10)
        order.reference = ''.join([random.choice('ABCDEFGHI') for _ in range(5)])
        order.cancel_date = end_date
        order.total_payment = grand_total_plus_shipping
        order.payment_method_id = form.payment_type.data
        # order.customer_id = (form.customer_id.data) if (form.customer_id.data) else (0)
        order.invoiceCreator_id = current_user.id
        order.at_delivery = form.address.data + ' - ' + form.city.data+ ', ' + form.country.data

        updateUser = User.query.get(current_user.id)
        updateUser.first_name = form.first_name.data
        updateUser.last_name = form.last_name.data
        updateUser.phoneNumber = form.phone_number.data

        form.populate_obj(order)
        db.session.add(order)
        db.session.commit()
        print('Order ID: ', order.id)

        for product in products:
            order_item = OrderDetails(unit_price=product['unit_price'],
                quantity=product['quantity'], book_id=product['id'], order_id=order.id)

            updateProduct = Book.query.filter_by(id=product['id']).update(
                {'available_quantity': Book.available_quantity - product['quantity']})
            # updateProduct = Book.query.filter_by(id=product['id']).first()
            # updateProduct = Book.query.get(product['id'])
            # updateProduct['available_quantity'] = updateProduct['available_quantity'] - product['quantity']
            
            db.session.add(order_item)

        db.session.commit()

        # remove the keyname from the session if it is there
        session['cart'] = []
        session.modified = True

        return redirect(url_for('orders.orderBooks'))
    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('checkout.html', form=form, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
