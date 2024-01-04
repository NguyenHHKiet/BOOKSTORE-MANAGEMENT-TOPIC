# Create dummy secrey key so we can use sessions
from urllib.parse import quote

SECRET_KEY = 'c007d6402c1b77b1fac427a381d995fd'

# Debug mode
DEBUG = True

# Create in-memory database

# DATABASE_FILE = 'bookstore'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/'+ DATABASE_FILE +'?charset=utf8mb4' % quote('admin')# Non_password_MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@localhost/bookstore?charset=utf8mb4' % quote('Bestpro890!@#')

# DATABASE_FILE = 'bookstore'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/'+ DATABASE_FILE +'?charset=utf8mb4' # Non_password_MySQL
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:%s@localhost/bookstore?charset=utf8mb4' % quote('admin')
# SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_TRACK_MODIFICATIONS = False


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


#VNPAY

VNPAY_TMN_CODE = "3VNWSZOD"
VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
VNPAY_HASH_SECRET_KEY= "EZMMDCWDQNUCFSMYYCHUIEQZGQRYCWDH"
VNPAY_RETURN_URL = "http://localhost:5000/payment_return"

#MAIL

MAIL_DEFAULT_SENDER = "dangdinhhuyisme@gmail.com"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = False
MAIL_USERNAME = "dangdinhhuyisme@gmail.com"
MAIL_PASSWORD = "kggq xlce prbq luvi"
