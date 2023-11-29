from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField

class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    country = SelectField('Country', choices=[('VN', 'VietNam'), ('KR', 'South Korean'), ('US', 'USA')])
    payment_type = SelectField('Payment Type', choices=[(1, 'Check'), (2, 'Wire Transfer'), (3, 'PayPal'), (4, 'Stripe')])
    customer_id = IntegerField('Customer ID', default=0)
