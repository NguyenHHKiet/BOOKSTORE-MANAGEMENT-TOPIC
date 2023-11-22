from flask import Flask, url_for, redirect, render_template, request, abort
from flask_admin.contrib import sqla
from flask_security import current_user
from flask_admin import expose, BaseView, AdminIndexView

# Create customized model view class
class MyModelView(sqla.ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    page_size = 20
    can_view_details = True
    def is_accessible(self):
        # roles with ascending permissions...
        if current_user.has_role('ADMIN'):
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
                current_user.has_role('ADMIN')
        )

        
# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.has_role('CUSTOMER'):
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
        arg1 = 'Hello CHART!'
        # Define Plot Data 
        labels = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
        ]
    
        data = [0, 10, 15, 8, 22, 18, 25]
        return self.render('admin/chart.html', arg1=arg1, data=data, labels=labels)
    
    

class ProductView( MyModelView):
    column_searchable_list = ['name']
    column_sortable_list = ['unit_price', 'available_quantity']
    column_filters = ['unit_price', 'name']
    can_export = True
    can_view_details = True

class OrderView( MyModelView):
    column_list = ['initiated_date',
                   'cancel_date',
                   'total_payment',
                   'received_money',
                   'paid_date',
                   'delivered_date',
                   'payment_method',
                   'order_details',
                   'customer ',
                   'staff']
    column_sortable_list = ['initiated_date', 'total_payment']
    column_searchable_list = ['initiated_date', 'total_payment']
    can_export = True
    can_view_details = True
    can_view_details=True

class UserView( MyModelView):
    column_list = ['id','username', 'password','fullname', 'email', 'phone', 'gender' , 'address', 'enable', 'avatar_src', 'create_at' , 'roles']
    column_searchable_list = ['username', 'email']
    column_filters = ['roles']
    can_export = True
    can_view_details = True