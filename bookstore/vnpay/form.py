from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import Length


class PaymentForm(FlaskForm):
    order_id = StringField("Order_id", validators=[Length(min=1, max=250)])
    order_type = StringField("Order_type", validators=[Length(min=1, max=20)], default="Bill payment")
    amount = IntegerField("Amount")
    order_desc = StringField("Description", validators=[Length(min=1, max=100)])
    bank_code = SelectField("Bank_code", choices=[("NCB", "NCB"), ("AGRIBANK", "Agribank"),
                                                  ("SCB", "SCB"), ("VIETCOMBANK", "Vietcombank"), ("BIDV", "BIDV"),
                                                  ("VISA", "Visa Card")])
    language = SelectField("Language", choices=[("vn", "Vietnamese"), ("en", "English")])
