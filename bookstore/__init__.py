import json
import traceback

from flask import Flask, render_template, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
import datetime

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.config['PAGE_SIZE'] = 6
app.config['COMMENT_SIZE'] = 5
@app.errorhandler(Exception)
def global_exception_handler(e):
    print(e)
    print(traceback.print_exc())
    return render_template("error_page.html", e=e)


# Create database connection object
db = SQLAlchemy(app)

from bookstore.models import Role, User, Configuration, Book, Category, Author, PaymentMethod, Comment

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from bookstore.main.routes import main
from bookstore.users.routes import users
from bookstore.books.routes import books
from bookstore.orders.routes import orders
from bookstore.cart.routes import cart

app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(books)
app.register_blueprint(orders)
app.register_blueprint(cart)
from bookstore import admin, utils

import cloudinary

cloudinary.config(
    cloud_name="ddgtjayoj",
    api_key="451466636224894",
    api_secret="8jP48b2XeCzhNdKNe9yGIwiDiN8"
)

from flask_mailman import Mail

mail = Mail(app)


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        anonymous_user = Role(name="anonymous")
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        staff_role = Role(name='staff')
        db.session.add_all([anonymous_user, super_user_role, user_role, staff_role])

        appconfig = Configuration(min_import_quantity=150,
                                  min_stock_quantity=300,
                                  time_to_end_order=48,

                                  quick_ship=0
                                  )
        db.session.add(appconfig)

        test_superuser = user_datastore.create_user(
            first_name='Admin',
            last_name='2023',
            email='admin@example.com',
            password=hash_password('admin'),
            roles=[staff_role, super_user_role],
            address='VN',
            confirmed_at=datetime.datetime.now(),
            phone_number="0795648319",
            active=True
        )
        test_staff = user_datastore.create_user(
            first_name='Staff',
            last_name='2023',
            email='staff@example.com',
            password=hash_password('staff'),
            roles=[staff_role],
            address='VN',
            confirmed_at=datetime.datetime.now(),
            phone_number="0798546948",
            active=True
        )
        test_user = user_datastore.create_user(
            first_name='user',
            last_name='2023',
            email='user@example.com',
            password=hash_password('user'),
            roles=[user_role],
            address='VN',
            confirmed_at=datetime.datetime.now(),
            phone_number="0986498464",
            active=True
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            phone = "0"
            for k in range(0, 9):
                phone += str(random.randint(6, 9))

            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=hash_password(tmp_pass),
                roles=[user_role, ],
                address='VN',
                confirmed_at=datetime.datetime.now(),
                phone_number=phone,
                active=True
            )



        # Book
        with open('bookstore/static/data_import/book_data.json', 'rb') as f:
            data = json.load(f)
            for book in data:
                name = str(book['title']).strip()
                category = str(book['category']).strip()
                author = str(book['author']).strip()
                description = str(book['description']).strip()
                image = str(book['image']).strip()
                db_category = Category.query.filter_by(name=category).first()
                if not db_category:
                    db_category = Category(name=category)
                    db.session.add(db_category)
                db_author = Author.query.filter_by(name=author).first()
                if not db_author:
                    db_author = Author(name=author)
                    db.session.add(db_author)
                db.session.commit()
                new_book = Book(name=name,
                                category=db_category,
                                author=db_author,
                                description=description,
                                image_src=image,
                                unit_price=random.randint(5, 15) * 1000,
                                available_quantity=random.randint(150, 200),
                                enable=True)
                db.session.add(new_book)
            db.session.commit()
        # payment method
        in_cash = PaymentMethod(name='CASH')
        internet_banking = PaymentMethod(name='BANKING')
        db.session.add_all([in_cash, internet_banking])
        db.session.commit()
        # Order
        staff_id = 2
        customer_list = User.query.filter(User.id > 2)
        book_list = Book.query.all()
        start_date = datetime.datetime(2023, 1, 1)
        days_increment = 0
        for customer in customer_list:
            random_number = random.randint(4, 7)
            order_details = []
            for i in range(0, random_number):
                b = random.choice(book_list)
                q = random.randint(1, 5)
                f = True
                for o in order_details:
                    if o['id'] == b.id:
                        o['quantity'] += q
                        f = False
                if f:
                    detail = {}
                    detail['id'] = b.id
                    detail['quantity'] = q
                    order_details.append(detail)
            initial_date = start_date + datetime.timedelta(days=days_increment)
            if days_increment > 30 * 12:
                days_increment = 0
            days_increment += 20
            order = utils.create_order(customer.id, staff_id, order_details, in_cash.id, initial_date)
            rand_num = random.randint(1, 10)
            utils.order_paid_incash(order.total_payment, order.id,
                                    order.initiated_date + datetime.timedelta(hours=rand_num))
            utils.order_delivered(order.id, order.initiated_date + datetime.timedelta(hours=rand_num + 1))

    for i in range(8):
                c = Comment(content=str(i+1), user_id=i+1, book_id=1)
                db.session.add(c)
                db.session.commit()
    return

# ImportError: cannot import name 'url_decode' from 'werkzeug.urls'
# error present werkzeug version 3.0, but flask_login not compatible yet version 3.0 (should werkzeug 2.3)
