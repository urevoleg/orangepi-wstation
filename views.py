from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request


class SensorView(ModelView):
    column_default_sort = ('loaded_at', True)

    """def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))"""
