# Create dummy secrey key so we can use sessions
SECRET_KEY = 'c007d6402c1b77b1fac427a381d995fd'

# Debug mode
DEBUG = True

# Create in-memory database
DATABASE_FILE = 'bookstore'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/'+ DATABASE_FILE +'?charset=utf8mb4' # Non_password_MySQL
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@localhost/bookstore?charset=utf8mb4' % quote('password_of_MySQLDatabase')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = True

# set optional bootswatch theme
FLASK_ADMIN_SWATCH = 'cerulean'

# set Flask-Security
# allows new registrations to application
SECURITY_REGISTERABLE = True