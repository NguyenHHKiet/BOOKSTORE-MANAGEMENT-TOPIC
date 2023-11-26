from flask_wtf import FlaskForm
from wtforms import StringField, SelectField

class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=[('NBI', 'Nairobi'), ('KMB', 'Kiambu')])
    country = SelectField('Country', choices=[('CE', 'Central'), ('RV', 'Rift Valley'), ('WE', 'Western')])
    payment_type = SelectField('Payment Type', choices=[('CK', 'Check'), ('WT', 'Wire Transfer')])

