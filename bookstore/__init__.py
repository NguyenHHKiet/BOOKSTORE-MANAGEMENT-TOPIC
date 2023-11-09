from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c007d6402c1b77b1fac427a381d995fd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bookstore?charset=utf8mb4' # Non_password_MySQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/bookstore?charset=utf8mb4' % quote('password_of_MySQLDatabase')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# account
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'


from bookstore import routes

# ImportError: cannot import name 'url_decode' from 'werkzeug.urls' 
# error present werkzeug version 3.0, but flask_login not compatible yet version 3.0 (should werkzeug 2.3)