import datetime

from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_security import logout_user, current_user, roles_accepted, login_required

import config
from bookstore.models import Order, Book, OrderDetails, User
from bookstore.orders.forms import Checkout
from bookstore.cart.utils import handle_cart
from bookstore import dao, utils
from bookstore.vnpay.form import PaymentForm
from bookstore.vnpay.vnpay import Vnpay

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

        if order.payment_method.name.__eq__("BANKING"):
            return redirect(url_for("orders.process_vnpay", order_id=order.id))

        return redirect(url_for('orders.orderBooks'))
    return render_template('checkout.html', form=form, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           quick_ship=configuration.quick_ship)


@orders.route("/vnpay", methods=["GET", "POST"])
def process_vnpay():
    form = PaymentForm()
    if request.method == 'POST':
        # Process input data and build url payment
        if form.validate_on_submit():
            order_type = form.order_type.data
            order_id = form.order_id.data
            amount = int(form.amount.data)
            order_desc = form.order_desc.data
            bank_code = form.bank_code.data
            language = form.language.data
            ipaddr = request.remote_addr
            # Build URL Payment
            vnp = Vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = config.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = str(order_id) + "_" + datetime.datetime.now().__str__()
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = config.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(config.VNPAY_PAYMENT_URL, config.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        order_id = int(request.args.get("order_id"))
        order = dao.get_order_by_id(order_id)
        if not order:
            flash("Order not found")
            return redirect(url_for("orders.checkout"))
        form.order_id.data = order.id
        form.amount.data = order.total_payment
        form.order_desc.data = "%s pay for bookstore online shopping" % (
                    current_user.first_name + current_user.last_name)
        return render_template("vnpay/payment.html", title="DISCHARGE", form=form)


@orders.route("/payment_return", methods=["GET"])
def payment_return():
    if request.args:
        vnp = Vnpay()
        vnp.responseData = request.args.to_dict()
        order_id = request.args.get('vnp_TxnRef')
        amount = int(request.args.get('vnp_Amount')) / 100
        order_desc = request.args.get('vnp_OrderInfo')
        vnp_BankTranNo = request.args.get("vnp_BankTranNo")
        vnp_TransactionNo = request.args.get('vnp_TransactionNo')
        vnp_ResponseCode = request.args.get('vnp_ResponseCode')
        vnp_PayDate = request.args.get('vnp_PayDate')
        vnp_BankCode = request.args.get('vnp_BankCode')
        vnp_CardType = request.args.get('vnp_CardType')
        vnp_SecureHash = request.args.get('vnp_SecureHash')
        if vnp.validate_response(config.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                utils.order_paid_by_vnpay(order_id=int(order_id[0:2:1]), bank_transaction_number=vnp_BankTranNo,
                                          vnpay_transaction_number=vnp_TransactionNo, bank_code=vnp_BankCode,
                                          card_type=vnp_CardType, secure_hash=vnp_SecureHash, received_money=amount,
                                          paid_date=vnp_PayDate)
                return render_template("vnpay/payment_return.html", title="Payment result",
                                       result="Success", order_id=order_id,
                                       amount=amount,
                                       order_desc=order_desc,
                                       vnp_TransactionNo=vnp_TransactionNo,
                                       vnp_ResponseCode=vnp_ResponseCode)
            else:
                return render_template("vnpay/payment_return.html", title="Payment result",
                                       result="Error", order_id=order_id,
                                       amount=amount,
                                       order_desc=order_desc,
                                       vnp_TransactionNo=vnp_TransactionNo,
                                       vnp_ResponseCode=vnp_ResponseCode)
        else:
            return render_template("vnpay/payment_return.html",
                                   title="Payment result", result="Error", order_id=order_id, amount=amount,
                                   order_desc=order_desc, vnp_TransactionNo=vnp_TransactionNo,
                                   vnp_ResponseCode=vnp_ResponseCode, msg="Wrong checksum")
    else:
        return render_template("vnpay/payment_return.html", title="Kết quả thanh toán", result="")
