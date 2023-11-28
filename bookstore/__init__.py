from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
import random

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('../config.py')

# Create database connection object
db = SQLAlchemy(app)

from bookstore.models import Role, User, Configuration, Book, Category, Author, PaymentMethod

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
from bookstore import admin


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
        
        check = PaymentMethod(name='Check')
        wireTransfer = PaymentMethod(name='Wire Transfer')
        payPal = PaymentMethod(name='PayPal')
        stripe = PaymentMethod(name='Stripe')
        db.session.add_all([check, wireTransfer, payPal, stripe])

        appconfig = Configuration(min_import_quantity=150,
                                  min_stock_quantity=300 ,
                                  time_to_end_order=48 ,
                                  time_to_end_register= 24)
        db.session.add(appconfig)

        test_superuser = user_datastore.create_user(
            first_name='Admin',
            email='admin@example.com',
            password=hash_password('admin'),
            roles=[staff_role, super_user_role]
        )
        test_staff = user_datastore.create_user(
            first_name='Staff',
            email='staff@example.com',
            password=hash_password('staff'),
            roles=[staff_role]
        )
        test_user = user_datastore.create_user(
            first_name='user',
            email='user@example.com',
            password=hash_password('user'),
            roles=[user_role]
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
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=hash_password(tmp_pass),
                roles=[user_role, ]
            )
        
        book_names = [
            'No Family', 'Miserables', 'The sound of birds singing in the thorn bush', 'To kill a mockingbird', 'Crime and Punishment', 'The Alchemist', 'Little Prince', 'Two Fates',
            'Godfather', 'Great Gatsby', 'Nauy forest', 'Three Great Teachers', 'Monk Sells Ferrari'
        ]
        category_names = [
            'Novel', 'Literature'
        ]
        author_names = [
            'Hector Malot', 'Victor Hugo', 'Colleen McCulough', 'Harper Lee', 'Fyodor Dostoevsky', 'Paulo Coelho', 'Antoine Saint – Exupéry', 'Jeffrey Archer',
            'Mario Puzo', 'Scott Fitzgerald', 'Haruki Murakami', 'Robin Sharam'
        ]
        
        # Create and add categories to the database
        for name in category_names:
            category = Category(name=name)
            db.session.add(category)
        db.session.commit()

        # Create and add authors to the database
        for name in author_names:
            author = Author(name=name)
            db.session.add(author)
        db.session.commit()
        
        # Retrieve IDs of categories and authors from the database
        category_ids = [category.id for category in Category.query.all()]
        author_ids = [author.id for author in Author.query.all()]
            
        for i in range(len(book_names)):
            book = Book(
                name=book_names[i],
                unit_price=random.randint(100, 1000),
                available_quantity=random.randint(50, 255),
                category_id=random.choice(category_ids),
                author_id=random.choice(author_ids),
                enable=True
            )
            db.session.add(book)
            
        db.session.commit()
    return

# ImportError: cannot import name 'url_decode' from 'werkzeug.urls' 
# error present werkzeug version 3.0, but flask_login not compatible yet version 3.0 (should werkzeug 2.3)