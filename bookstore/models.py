from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from bookstore import db
from flask_security import RoleMixin, UserMixin

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(64), nullable=False, default=email)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    phoneNumber = db.Column(db.String(20))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)

    def __str__(self):
        return self.email


class Configuration(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    min_import_quantity = Column(Integer, nullable=False)
    min_stock_quantity = Column(Integer, nullable=False)
    time_to_end_order = Column(Integer, nullable=False)
    time_to_end_register = Column(Integer, nullable=False)



class RegisterCode(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    enable = Column(Boolean, nullable=False, default=True)
    expired_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship("User", uselist=False)

class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship("Book", backref='category', lazy=True)
    def __str__(self):
        return self.name

class Author(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship("Book", backref='author', lazy=True)
    def __str__(self):
        return self.name



class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    unit_price = Column(Integer, nullable=False, default=0)
    available_quantity = Column(Integer, nullable=False)
    image_src = Column(LONGTEXT, nullable=True, default='default.jpg')
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    author_id = Column(Integer, ForeignKey(Author.id), nullable=False)
    import_details = relationship("ImportDetails", backref='book', lazy=True)
    order_details = relationship("OrderDetails", backref= 'book', lazy= True)
    enable = Column(Boolean, nullable=False, default=False)
    description = db.Column(LONGTEXT)
    
    def in_stock(self):
        if db.session:
            item = []
            try:
                item = db.session['cart']
            except:
                pass
            index = 0
            if len(item) > 0:
                for ind, it in enumerate(item):
                    if it.get('id') == self.id:
                        index = ind
                return self.available_quantity - item[index].get('quantity')
            else:
                return self.available_quantity
        else:
            return self.available_quantity

class ImportTicket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    import_date = Column(DateTime, nullable=False, default=func.now())
    details = relationship("ImportDetails", backref='import_ticket', lazy=False)

class ImportDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    import_ticket_id = Column(Integer, ForeignKey(ImportTicket.id), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)

class PaymentMethod(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)

class Order(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    initiated_date = Column(DateTime, nullable=False)
    cancel_date = Column(DateTime,nullable=False)
    total_payment = Column(Integer, nullable=False)
    received_money = Column(Integer, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    delivered_date = Column(DateTime, nullable=True, default=None)
    payment_method_id = Column(Integer, ForeignKey(PaymentMethod.id), nullable=False)
    payment_method =  relationship("PaymentMethod", uselist=False)
    order_details = relationship("OrderDetails", backref="order", lazy=False)
    customer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    customer = relationship("User", foreign_keys=customer_id, backref='bought')
    staff_id = Column(Integer, ForeignKey(User.id), nullable=False)
    staff = relationship("User", foreign_keys=staff_id, backref='managed')
    
    def order_total(self):
        return db.session.quey(db.func.sum(OrderDetails.quantity * Book.unit_price)).join(Book).filter(OrderDetails.order_id == self.id).scalar() + 1000

    def quantity_total(self):
        return db.session.query(db.func.sum(OrderDetails.quantity)).filter(OrderDetails.order_id == self.id).scalar()

class OrderDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey(Order.id), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)