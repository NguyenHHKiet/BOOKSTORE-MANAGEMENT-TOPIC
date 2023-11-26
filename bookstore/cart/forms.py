from flask_wtf import FlaskForm
from wtforms import IntegerField, HiddenField

class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = IntegerField('ID')
