from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login as login
from werkzeug.security import generate_password_hash, check_password_hash

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('../config.py')

# Create database connection object
db = SQLAlchemy(app)

from bookstore.models import Role, User

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)
    
from bookstore.main.routes import main
from bookstore.users.routes import users
app.register_blueprint(main)
app.register_blueprint(users)

# Initialize flask-login
init_login()

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
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        staff_role = Role(name='staff')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.add(staff_role)
        db.session.commit()

        test_admin = User(
            first_name='Admin',
            email='admin@example.com',
            password=generate_password_hash('admin'),
            roles=[staff_role, super_user_role]
        )
        db.session.add(test_admin)

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
            user = User(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=generate_password_hash(tmp_pass),
                roles=[user_role, ]
            )
            db.session.add(user)
        db.session.commit()
    return

# ImportError: cannot import name 'url_decode' from 'werkzeug.urls' 
# error present werkzeug version 3.0, but flask_login not compatible yet version 3.0 (should werkzeug 2.3)