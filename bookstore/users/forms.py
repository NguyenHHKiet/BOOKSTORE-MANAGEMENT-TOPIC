
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_security import current_user
from flask_security.utils import verify_password
from bookstore.models import User
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
    def get_user(self):
        return User.query.filter_by(email=self.email.data).first()
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Invalid email. Email doesn't exist!!!")
        
    def validate_password(self, password):
        user = self.get_user()
        if user and not verify_password(password.data, user.password):
            raise ValidationError("Invalid password. Passwords do not match!!!")
        
    def get_user(self):
        return User.query.filter_by(email=self.email.data).first()
class UpdateAccountForm(FlaskForm):
    firstname = StringField("Firstname", validators=[DataRequired()])
    lastname = StringField("Lastname", validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    gender = RadioField("Gender", choices=[(1, 'Male'), (0, "Female")])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_phone(self, phone):
        if not phone.data:
            raise ValidationError("Phone can't be empty")
        if not phone.data.isdigit():
            raise ValidationError("Phone must be digit only")
        if len(phone.data) != 0:
            raise ValidationError("Length is invalid")
        if phone.data[0] != "0":
            raise ValidationError("Phone must start with 0")

class VerifyAccountForm(FlaskForm):
    first_char = StringField("First", validators=[DataRequired()], render_kw={"maxlength": 1})
    second_char = StringField("Second", validators=[DataRequired()], render_kw={"maxlength": 1})
    third_char = StringField("Third", validators=[DataRequired()], render_kw={"maxlength": 1})
    fourth_char = StringField("Fourth", validators=[DataRequired()], render_kw={"maxlength": 1})
    fifth_char = StringField("Fifth", validators=[DataRequired()], render_kw={"maxlength": 1})
    submit = SubmitField("Verify")

    def to_code(self):
        return self.fifth_char.data + self.second_char.data + self.third_char.data + self.fourth_char.data + self.fifth_char.data
    