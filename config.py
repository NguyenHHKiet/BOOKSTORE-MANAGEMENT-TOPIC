# Create dummy secrey key so we can use sessions
from urllib.parse import quote

SECRET_KEY = 'c007d6402c1b77b1fac427a381d995fd'

# Debug mode
DEBUG = True

# Create in-memory database
DATABASE_FILE = 'bookstore'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/'+ DATABASE_FILE +'?charset=utf8mb4' # Non_password_MySQL
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:%s@localhost/bookstore?charset=utf8mb4' % quote('admin')

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = True