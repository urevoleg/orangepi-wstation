import json

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=data['loaded_at'], y=data['t'],
                       mode='lines+markers',
                       line=dict(width=0.75),
                       marker=dict(size=5),
                       name='Temperature'),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=data['loaded_at'], y=data['p'],
                       mode='lines+markers',
                       line=dict(width=0.75),
                       marker=dict(size=5),
                       name='Pressure'),
            secondary_y=True,
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Дата")

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Temperature</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Pressure</b>", secondary_y=True)
        # Add figure title
        fig.update_layout(template='plotly_white',
                          title='Sensor data',
                          showlegend=True)

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return self.render(template='admin/index.html', graphJSON=graphJSON)
