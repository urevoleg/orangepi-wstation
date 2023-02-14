import json

import plotly
import plotly.express as px

from collections import defaultdict

from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for, request

from app import app, db


class SensorView(ModelView):
    column_default_sort = ('loaded_at', True)

    """def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))"""


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        with app.app_context():
            with db.engine.connect() as conn:
                stmt = """with raw as (select loaded_at, 
                                                cast(json_data::json->> 'l' as int) as l, 
                                                0.01 * cast(json_data::json->> 't' as int) as t, 
                                                0.1 * cast(json_data::json->> 'p' as int) as p
                                        from sensors
                                        where loaded_at > now() - interval '6h'
                                        and category = 'weather-out'
                                        order by loaded_at desc)
                            select *
                            from raw
                            order by loaded_at;"""
                res = conn.execute(stmt)

                data = defaultdict(list)
                for row in res.fetchall():
                    for k, v in row.items():
                        data[k] += [v]

        fig = px.line(data, x='loaded_at', y='t')
        fig.update_layout(template='plotly_white')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return self.render(template='admin/index.html', graphJSON=graphJSON)