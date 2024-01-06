import os
from datetime import timedelta, datetime

import pandas
from flask import current_app
from bookstore import dao
from bookstore.models import ImportTicket, Category, Author, Book, ImportDetails, OrderDetails, Order
import cloudinary.uploader


def import_book(excel):
    # save file

    response = cloudinary.uploader.upload(excel, resource_type="auto", format="xlsx")
    file_url = response['secure_url']
    # read data
    data = pandas.read_excel(excel)
    # handle new book data
    # save ticket
    ticket = dao.save_ticket(url=file_url)

    # get bookstore configuration
    configuration = dao.get_configuration()
    for index, row in data.iterrows():
        name = str(row['Name']).strip()
        category = str(row['Category']).strip()
        author = str(row['Author']).strip()
        quantity = int(row['Quantity'])
        # check the quantity is valid or not
        if quantity < configuration.min_import_quantity:
            continue
        # query book from database if not exist then create
        db_book = dao.get_book_by_name(name=name)
        if not db_book:
            db_category = dao.get_category_by_name(name=category)
            if not db_category:
                db_category = Category(name=category)
                dao.save_category(db_category)
            db_author = dao.get_author_by_name(name=author)
            if not db_author:
                db_author = Author(name=author)
                dao.save_author(db_author)
            db_book = Book(name=name, author=db_author, category=db_category, available_quantity=quantity)
            dao.save_book(book=db_book)
        else:
            # check in stock quantity
            if db_book.available_quantity > configuration.min_stock_quantity:
                continue
            else:
                db_book.available_quantity += quantity
                dao.save_book(book=db_book)
        # save ticket details
        ticket_details = ImportDetails(quantity=quantity, book=db_book, import_ticket=ticket)
        dao.save_ticket_details(ticket_details=ticket_details)


def statistic_revenue():
    return [data[0] for data in dao.statistic_revenue()]


def statistic_book_by_month(month):
    sql_result = dao.stat_book_by_month(month)
    if sql_result is None:
        return None
    total_quantity = 0
    for res in sql_result:
        total_quantity += res[2]
    data = []
    index = 1
    for res in sql_result:
        temp = {}
        temp['index'] = index
        temp['name'] = res[0]
        temp['category'] = res[1]
        temp['quantity'] = res[2]
        temp['percentage'] = round((res[2] / total_quantity) * 100, 2)
        data.append(temp)
        index += 1
    return data


def statistic_category_by_month(month):
    sql_result = dao.stat_category_by_month(month)
    if sql_result is None:
        return None

    total_revenue = 0
    for res in sql_result:
        total_revenue += res[2]
    data = []
    index = 1
    for res in sql_result:
        temp = {}
        temp['index'] = index
        temp['name'] = res[0]
        temp['revenue'] = res[2]
        temp['number_of_purchases'] = res[1]
        temp['percentage'] = round((res[2] / total_revenue) * 100, 2)
        data.append(temp)
        index += 1
    return data


def create_order(customer_id, staff_id, books, payment_method_id, initial_date=datetime.now()):
    configuration = dao.get_configuration()
    customer = dao.get_user_by_id(customer_id)
    staff = dao.get_user_by_id(staff_id)
    payment_method = dao.get_payment_method_by_id(payment_method_id)
    # create order details
    order_details = []
    total_payment = 0
    for ordered_book in books:
        book = dao.get_book_by_id(ordered_book['id'])
        if book is not None:
            detail = OrderDetails(unit_price=book.unit_price, quantity=ordered_book['quantity'], book=book)
            total_payment += book.unit_price * ordered_book['quantity']
            order_details.append(detail)
            book.available_quantity -= ordered_book['quantity']
            dao.save_book(book)
    # create order
    if payment_method.name.__eq__("BANKING"):
        total_payment += configuration.quick_ship
    order = Order(cancel_date=initial_date + timedelta(hours=configuration.time_to_end_order),
                  payment_method=payment_method,
                  customer=customer,
                  staff=staff,
                  total_payment=total_payment,
                  initiated_date=initial_date,
                  delivery_at=customer.address
                  )

    dao.save_order(order)
    for od in order_details:
        od.order = order
        dao.save_order_details(od)
    return order


def order_paid_incash(received_money, order_id, paid_date=datetime.now()):
    order = dao.get_order_by_id(order_id)
    if order is None or order.paid_date:
        return -1
    if received_money < order.total_payment:
        return -2
    order.received_money = received_money
    order.paid_date = paid_date
    dao.save_order(order)
    return 0


def order_paid_by_vnpay(order_id, bank_transaction_number, vnpay_transaction_number, bank_code, card_type,
                        secure_hash, received_money, paid_date):
    order = dao.get_order_by_id(order_id)
    if not order or order.paid_date:
        return -1
    else:
        infor = dao.save_banking_information(order_id=order_id, bank_transaction_number=bank_transaction_number,
                                             vnpay_transaction_number=vnpay_transaction_number, bank_code=bank_code,
                                             card_type=card_type, secure_hash=secure_hash)
        if infor:
            order.received_money = received_money
            order.paid_date = paid_date
            dao.save_order(order)
            return 0


def order_delivered(order_id, delivered_date=datetime.now()):
    order = dao.get_order_by_id(order_id)
    if order is None:
        return -1
    order.delivered_date = delivered_date
    dao.save_order(order)
    return 0


def handle_order_details(order_id):
    order = dao.get_order_by_id(order_id)
    if not order:
        return None
    else:

        products = []
        grand_total = 0
        index = 0
        order_quantity_total = 0
        for detail in order.order_details:
            book = detail.book
            quantity = detail.quantity
            total = detail.quantity * detail.unit_price

            order_quantity_total += quantity
            grand_total += total

            products.append({'id': book.id, 'name': book.name, 'unit_price': book.unit_price,
                             'image_src': book.image_src, 'quantity': quantity, 'total': total, 'index': index})
            index += 1

        grand_total_plus_shipping = order.total_payment
        quick_ship = grand_total_plus_shipping - grand_total if grand_total_plus_shipping - grand_total >= 0 else None
        isPaid = True if (order.paid_date is not None) and (order.received_money is not None) else False
        isDelivered = True if order.delivered_date is not None else False
        isCanceled = True if (order.paid_date is None) and (order.cancel_date < datetime.now()) else False
        return products, grand_total, grand_total_plus_shipping, order_quantity_total, quick_ship, isPaid, isDelivered, isCanceled

def truncate_text(text, max_length=300):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text