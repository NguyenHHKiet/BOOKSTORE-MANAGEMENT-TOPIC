from flask import Flask, url_for, redirect, render_template, request, abort
from flask_admin.contrib import sqla
from flask_security import current_user
from flask_admin import expose, BaseView, AdminIndexView
from bookstore.models import Order, OrderDetails, Book
import random

# Create customized model view class
class MyModelView(sqla.ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    page_size = 20
    can_view_details = True
    def is_accessible(self):
        # roles with ascending permissions...
        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        return False
    

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
    
class AuthenticatedView(BaseView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('staff')
        )
        
class UserAdmin(MyModelView):
    column_list = ('first_name', 'email', 'roles')
    column_labels = {'first_name': 'First Name', 'email': 'Email Address', 'roles': 'Role'}
    column_filters = ('first_name', 'email', 'roles.name')

class RoleAdmin(MyModelView):
    column_list = ('name',)
    column_labels = {'name': 'Role Name'}
    column_filters = ('name',)
        
# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.has_role('user'):
            return redirect(url_for('main.home'))
        
        # if not current_user.is_authenticated:
        #     return redirect(url_for('security.login'))
        arg1 = 'Hello INDEX!'
        err_msg = 'Hiện tại bạn chưa đăng nhập vào! Vui lòng đăng nhập!'
        self._template_args['err_msg'] = err_msg
        self._template_args['arg1'] = arg1
        return self.render('admin/index.html')
    
class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        data = []
        labels = []
        arg1 = 0
        arg2 = 0
        itemsCount = {}
        book_list = []
        book_label = []
        # Define Plot Data 
        orders = Order.query.all()
        orderDetails = OrderDetails.query.all()
        books = Book.query.all()
        for order in orders:
            arg1 = arg1 + order.total_payment
            data.append(order.total_payment/100)
            labels.append(order.initiated_date)
        
        for od in orderDetails:
            if od.book_id in itemsCount:
                print('Key exists')
                itemsCount[od.book_id] += 1
            else:
                print('Key does not exist')
                itemsCount[od.book_id] = 1

        for book in books:
            book_label.append(book.name)
            if book.id in itemsCount:
                arg2 += itemsCount[book.id]
                book_list.append(itemsCount[book.id])
            else:
                book_list.append(0)
        
        colors = []
        for i in range(len(book_label)):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            colors.append(f"rgb({r}, {g}, {b})")
        
        self._template_args['arg1'] = arg1 / 100
        self._template_args['arg2'] = arg2
        self._template_args['book_label'] = book_label
        self._template_args['book_list'] = book_list
        self._template_args['colors'] = colors
        return self.render('admin/chart.html', data=data, labels=labels)

class ProductView(MyModelView):
    column_list = ('id', 'name', 'unit_price','available_quantity','enable','category.name','author.name')
    column_labels = {'id':'ID','name': 'Book Name', 'unit_price': 'Unit Price',
                     'available_quantity': 'Available Quantity','enable': 'Enable'
                     ,'category.name':'Category'
                     ,'author.name':'Author'}
    column_searchable_list = ['name']
    column_sortable_list = ['unit_price', 'available_quantity']
    column_filters = ['unit_price', 'name']

class OrderView(MyModelView):
        column_list = ['id','initiated_date',
                       'cancel_date',
                       'total_payment',
                       'received_money',
                       'paid_date',
                       'delivered_date',
                       'payment_method.name',
                       'order_details',
                       'invoiceCreator.email',
                       'state',
                       'reference',
                       'at_delivery']
        column_labels = {'payment_method.name':'Payment Method', 
                         'invoiceCreator.email': 'Owner Email',
                         'order_details': 'Order Details',}
        column_searchable_list = ['state', 'invoiceCreator.email']
        column_sortable_list = ['initiated_date', 'total_payment']
        column_filters = ['payment_method.name', 'state', 'invoiceCreator.email']

class BookImportView(AuthenticatedView):
    @expose('/')
    def index(self):
       return self.render('/admin/import.html')

class ConfigurationView(MyModelView):
    column_list = ['min_import_quantity', 'min_stock_quantity', 'time_to_end_order', 'time_to_end_register']
    can_delete = False
    can_create = False

