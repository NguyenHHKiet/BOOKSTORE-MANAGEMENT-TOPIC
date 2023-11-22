from flask import Flask, url_for, redirect, render_template, request, abort
from flask_admin.contrib import sqla
from flask_security import current_user
from flask_admin import expose, AdminIndexView, BaseView, helpers
from bookstore import db
from bookstore.users.forms import LoginForm, RegistrationForm
from bookstore.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login as login

# Create customized model view class
class MyModelView(sqla.ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    page_size = 20
    can_view_details = True
    def is_accessible(self):
        # roles with ascending permissions...
        if current_user.is_authenticated:
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
                return redirect(url_for('.login_view', next=request.url))
    
class AuthenticatedView(BaseView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated
        )
        
# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        arg1 = 'Hello INDEX!'
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        self._template_args['arg1'] = arg1
        return super(MyAdminIndexView, self).index()
    
    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        print(login.current_user.is_authenticated)
        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


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