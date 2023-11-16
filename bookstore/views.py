from flask import Flask, url_for, redirect, render_template, request, abort
from flask_admin.contrib import sqla
from flask_security import current_user
from flask_admin import expose, AdminIndexView, BaseView
    
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
                current_user.has_role('superuser')
        )
        
# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        arg1 = 'Hello INDEX!'
        
        # if not current_user.is_authenticated:
        #     return redirect(url_for('security.login'))
        return self.render('admin/index.html', arg1=arg1)


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