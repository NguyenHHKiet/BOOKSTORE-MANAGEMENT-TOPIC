from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('../config.py')

# Create database connection object
db = SQLAlchemy(app)

from bookstore.models import Role, User

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from bookstore.main.routes import main
from bookstore.users.routes import users
app.register_blueprint(main)
app.register_blueprint(users)

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
        customer_role = Role(name='CUSTOMER')
        admin_role = Role(name='ADMIN')
        staff_role = Role(name='STAFF')
        db.session.add(customer_role)
        db.session.add(admin_role)
        db.session.add(staff_role)
        db.session.commit()

        admin_user = user_datastore.create_user(
            username='admin',
            email='admin@example.com',
            password=hash_password('admin'),
            fullname= 'exampleadmin',
            phone= '0789640313',
            gender = True,
            address='HCM',
            active=True,
            image_file='',
            roles=[admin_role]
        )
        staff_user = user_datastore.create_user(
            username='staff',
            email='staff@example.com',
            password=hash_password('staff'),
            fullname= 'examplestaff',
            phone= '013245454',
            gender = True,
            address='HCM',
            active=True,
            image_file='',
            roles=[staff_role]
        )
        customer_user = user_datastore.create_user(
            username='customer',
            email='customer@example.com',
            password=hash_password('customer'),
            fullname= 'examplecustomer',
            phone= '0354849566',
            gender = True,
            address='HCM',
            active=True,
            image_file='',
            roles=[customer_role]
        )

        db.session.commit()
    return

# ImportError: cannot import name 'url_decode' from 'werkzeug.urls' 
# error present werkzeug version 3.0, but flask_login not compatible yet version 3.0 (should werkzeug 2.3)