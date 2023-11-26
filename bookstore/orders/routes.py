from flask import Blueprint,render_template, redirect, url_for, flash
from flask_security import logout_user, current_user, roles_accepted, login_required
from bookstore.models import Order, Book, OrderDetails
from bookstore.orders.forms import Checkout
from bookstore.cart.utils import handle_cart
from bookstore import db
import random, datetime

orders = Blueprint('orders', __name__)


@orders.route("/orders")
def orderBooks():
    if not current_user.is_authenticated:
        flash(f'You have not been logged in yet. Please login now!', 'warning')
        return redirect(url_for("users.login"))
    return render_template('orderBooks.html', title='Order Books')

@orders.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # if not current_user.is_authenticated:
    #     flash(f'You have not been logged in yet. Please login now!', 'warning')
    #     return redirect(url_for("users.login"))
    
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    if form.validate_on_submit():

        order = Order()
        form.populate_obj(order)
        end_date = datetime.date.today() + datetime.timedelta(days=10)
        # order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        order.status = 'PENDING'
        order.cancel_date = end_date
        order.total_payment = grand_total_plus_shipping

        # db.session.add(order)
        print(order.id)

        # for product in products:
        #     order_item = OrderDetails(unit_price=product['unit_price'],
        #         quantity=product['quantity'], book_id=product['id'], order_id=order.id)
        #     order.items.append(order_item)

        #     product = Book.query.filter_by(id=product['id']).update(
        #         {'available_quantity': Book.available_quantity - product['quantity']})
            
        #     db.session.add([order_item, product])

        # # db.session.commit()

        # db.session['cart'] = []
        # db.session.modified = True

        # return redirect(url_for('orders.orderBooks'))

    return render_template('checkout.html', form=form, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)
