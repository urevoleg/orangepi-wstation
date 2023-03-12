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
                stmt = """with raw as (select date_trunc('minute', loaded_at) as loaded_at, 
                                                avg(cast(json_data::json->> 'l' as float)) as l, 
                                                avg(0.01 * cast(json_data::json->> 't' as int)) as t, 
                                                round(avg(avg(0.1 * cast(json_data::json->> 'p' as int))) over(order by date_trunc('minute', loaded_at) range between '5min' preceding and current row), 2) as p
                                        from sensors
                                        where loaded_at > now() - interval '12h'
                                        and category = 'weather-out'
                                        group by 1
                                        order by loaded_at)
                            select *
                            from raw
                            order by loaded_at;"""
                res = conn.execute(stmt)

                data = defaultdict(list)
                for row in res.fetchall():
                    for k, v in row.items():
                        data[k] += [v]
        # indicators
        # Create figure with secondary y-axis
        fig_indicators = go.Figure()

        # Add traces
        fig_indicators.add_trace(
            go.Indicator(
                value=data['t'][-1],
                title={"text": "<b>Temperature</b>"},
                domain={'row': 0, 'column': 0},
                number={'font': {'size': 48}, "suffix": "°"}
            ),
        )

        fig_indicators.add_trace(
            go.Indicator(
                mode="number+delta",
                title={"text": "<b>Pressure</b>"},
                value=sum(data['p'][-5:]) / 5,
                delta={'reference': sum(data['p'][-65:-60])/5, 'relative': False, 'valueformat': '.2f'},
                domain={'row': 0, 'column': 1},
                number={'font': {'size': 48}, "suffix": "mmHg"}
            )
        )

        fig_indicators.add_trace(
            go.Indicator(
                mode="number",
                title={"text": "<b>Light</b>"},
                value=data['l'][-1],
                domain={'row': 0, 'column': 2},
                number={'font': {'size': 48}, "suffix": "lx"}
            ),
        )

        # Add figure title
        fig_indicators.update_layout(template='plotly_white',
                                     grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
                                     height=180)
        indicatorJSON = json.dumps(fig_indicators, cls=plotly.utils.PlotlyJSONEncoder)

        # plots
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
                          showlegend=True,
                          height=720)

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return self.render(template='admin/index.html',
                           graphJSON=graphJSON,
                           indicatorJSON=indicatorJSON)
