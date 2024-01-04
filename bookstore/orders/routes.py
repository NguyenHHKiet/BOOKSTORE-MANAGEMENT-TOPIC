import datetime

from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify, abort
from flask_security import logout_user, current_user, roles_accepted, login_required

import config

from bookstore.orders.forms import Checkout
from bookstore.cart.utils import handle_cart
from bookstore import dao, utils
from bookstore.vnpay.form import PaymentForm
from bookstore.vnpay.vnpay import Vnpay

orders = Blueprint('orders', __name__)


@orders.route("/orders")
@login_required
def orderBooks():
    orders = dao.get_orders_by_customer_id(current_user.id)
    return render_template('orderBooks.html', title='Order Books', orders=orders, datetime=datetime.datetime)


@orders.route("/order_details", methods=['GET'])
@login_required
def view_order_details():
    order_id = int(request.args.get("order_id"))
    products, grand_total, grand_total_plus_shipping, order_quantity_total, quick_ship, isPaid, isDelivered, isCanceled = utils.handle_order_details(
        order_id)
    return render_template("order_details.html", products=products, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping,
                           order_quantity_total=order_quantity_total,
                           quick_ship=quick_ship)


@orders.route("/api/order_details")
@login_required
def get_order_details():
    order_id = int(request.args.get("order_id"))
    if order_id:
        products, grand_total, grand_total_plus_shipping, order_quantity_total, quick_ship, isPaid, isDelivered, isCanceled = utils.handle_order_details(
            order_id)
        return jsonify({
            "order_id": order_id,
            "products": products,
            "grand_total": grand_total,
            "grand_total_plus_shipping": grand_total_plus_shipping,
            "order_quantity_total": order_quantity_total,
            "quick_ship": quick_ship,
            "isPaid": isPaid,
            "isDelivered": isDelivered,
            "isCanceled": isCanceled
        })
    else:
        abort(400)


@orders.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    configuration = dao.get_configuration()
    payment_methods = dao.get_payment_method_all()
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    form = Checkout()
    form.payment_type.choices = [(method.id, method.name) for method in payment_methods]
    if request.method == "GET":
        customer = None
        # in table order request
        if (request.args.get("staff_id") is not None) and (request.args.get("customer_phone")):
            if int(request.args.get("staff_id")) == current_user.id:
                customer_phone = request.args.get("customer_phone")
                if customer_phone:
                    customer = dao.get_user_by_phone(customer_phone)
                else:
                    customer = dao.get_user_by_username("user@example.com")

            else:
                flash("Can't create order", "danger")
                return redirect(url_for("users.staff"))
        # online
        else:
            customer = current_user
        form.customer_id.data = customer.id
        form.full_name.data = customer.first_name + " " + customer.last_name
        form.phone_number.data = customer.phone_number
        form.email.data = customer.email
        form.address.data = customer.address
    elif form.validate_on_submit():
        customer = None
        staff = None
        # in table order
        if int(form.customer_id.data) != current_user.id:
            customer = dao.get_user_by_id(int(form.customer_id.data))
            staff = current_user
        # online order
        else:
            customer = current_user
            # staff is the one who managed online order, has username = staff@example.com
            staff = dao.get_user_by_username("staff@example.com")
        order = utils.create_order(customer.id, staff.id, session['cart'], form.payment_type.data)
        session['cart'] = []
        session.modified = True

        if (current_user.id != customer.id):
            if (order.payment_method.name.__eq__("CASH")):
                flash("New order has been created", "success")
                return redirect(url_for("users.staff"))
        else:
            if current_user.phone_number != form.phone_number.data or current_user.address != form.address.data:
                update_user = dao.get_user_by_id(current_user.id)
                update_user.phone_number = form.phone_number.data
                update_user.address = form.address.data
                dao.save_user(update_user)

        if order.payment_method.name.__eq__("BANKING"):
            return redirect(url_for("orders.process_vnpay", order_id=order.id, user_id=customer.id))

        else:
            return redirect(url_for('orders.orderBooks'))

    return render_template('checkout.html', form=form, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total,
                           quick_ship=configuration.quick_ship)


@orders.route("/vnpay", methods=["GET", "POST"])
@login_required
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
        user_id = int(request.args.get("user_id"))
        order = dao.get_order_by_id(order_id)
        user = dao.get_user_by_id(user_id)
        if not order:
            flash("Order not found", "danger")
            return redirect(url_for("orders.checkout"))
        if not user:
            flash("User not found", "danger")
            return redirect(url_for("orders.checkout"))
        form.order_id.data = order.id
        form.amount.data = order.total_payment
        form.order_desc.data = "%s pay for bookstore online shopping" % (
                user.first_name + user.last_name)
        return render_template("vnpay/payment.html", title="DISCHARGE", form=form)


@orders.route("/payment_return", methods=["GET"])
@login_required
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


@orders.route("/api/order_delivered", methods=["POST"])
@login_required
def order_delivered():
    try:
        order_id = int(request.args.get("order_id"))
        if utils.order_delivered(order_id) == 0:
            return jsonify({"code": 200, "order_id": order_id})
        else:
            return jsonify({"code": 400, "order_id": order_id})
    except:
        return jsonify({"code": 500, "order_id": order_id})


@orders.route("/api/order/cash/pay", methods = ["POST"])
def intable_pay_order():
    try:

        order_id = int(request.json.get("order_id"))
        received_money = int(request.json.get("received_money"))
        print(order_id, received_money)
        if utils.order_paid_incash(received_money, order_id) == 0:
            utils.order_delivered(order_id)
            return jsonify({"code": 200})
        else:
            return jsonify({"code": 402})
    except Exception as e:
        print(e)
        return jsonify({"code": 400})
