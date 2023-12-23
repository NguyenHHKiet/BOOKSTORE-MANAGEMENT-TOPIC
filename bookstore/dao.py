from sqlalchemy import text

from bookstore import db
from bookstore.models import Configuration, ImportTicket, Book, Category, Author, PaymentMethod, User, Order


def get_configuration():
    return Configuration.query.first()

def save_ticket(ticket):
    db.session.add(ticket)
    db.session.commit()

def get_book_by_name(name):
    return Book.query.filter_by(name=name).first()

def save_book(book):
    db.session.add(book)
    db.session.commit()

def get_category_by_name(name):
    return Category.query.filter_by(name=name).first()

def save_category(category):
    db.session.add(category)
    db.session.commit()

def get_author_by_name(name):
    return Author.query.filter_by(name=name).first()

def save_author(author):
    db.session.add(author)
    db.session.commit()

def save_ticket_details(ticket_details):
    db.session.add(ticket_details)
    db.session.commit()

def get_payment_method_by_id(id):
    return PaymentMethod.query.get(id)

def get_user_by_id(id):
    return User.query.get(id)

def get_book_by_id(id):
    return Book.query.get(id)

def save_order(order):
    db.session.add(order)
    db.session.commit()

def save_order_details(order_detail):
    db.session.add(order_detail)
    db.session.commit()

def get_order_by_id(order_id):
    return Order.query.get(order_id)


def stat_book_by_month(month):
    return db.session.execute(text("SELECT book.name, category.name AS category,  SUM(order_details.quantity) AS quantity "
                                   "FROM  bookstore.book "
                                   "JOIN bookstore.order_details "
                                   "ON book.id = order_details.book_id "
                                   "JOIN bookstore.order "
                                   "ON order_details.order_id = bookstore.order.id "
                                   "JOIN bookstore.category "
                                   "ON book.category_id = category.id "
                                   "WHERE month(bookstore.order.paid_date) = 2 "
                                   "GROUP BY book.name "
                                   "ORDER BY quantity"), {"month": month}).all()

def stat_category_by_month(month):
    return db.session.execute(text("SELECT category.name, count(order_details.book_id) AS number_of_purchases, SUM(order_details.quantity * order_details.unit_price) AS revenue "
                                   "FROM  bookstore.category "
                                   "LEFT JOIN bookstore.book ON category.id = book.category_id "
                                   "LEFT JOIN bookstore.order_details ON book.id = order_details.book_id "
                                   "JOIN bookstore.order ON order_details.order_id = bookstore.order.id "
                                   "WHERE month(bookstore.order.paid_date) = :month "
                                   "GROUP BY category.name "
                                   "ORDER BY revenue DESC"), {"month": month}).all()

def statistic_revenue():
    return db.session.execute(text("SELECT SUM(total_payment) AS revenue "
                                   "FROM bookstore.order "
                                   "GROUP BY month(paid_date) "
                                   "ORDER BY month(paid_date)")).all()