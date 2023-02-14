import os
import datetime as dt
import json


from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from flask_apscheduler import APScheduler

from sensor_reader.reader import SensorReader

from config import Config, SensorsConfig


# init Flask
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, session_options={'autocommit': False})


class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True, index=True)
    category = db.Column(db.String, nullable=False)
    json_data = db.Column(db.TEXT)
    loaded_at = db.Column(db.DateTime, default=dt.datetime.now)

    def __repr__(self):
        return f"Sensor(id={self.id}, category={self.category}, json_data={self.json_data}, loaded_at={self.loaded_at})"

import json

import plotly
import plotly.express as px

import pandas as pd

from flask_admin import AdminIndexView, expose
import views


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
                df = pd.DataFrame(res.fetchall())

        fig = px.line(df, x='loaded_at', y='t')
        fig.update_layout(template='plotly_white')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return self.render('admin/index.html', graphJSON=graphJSON, title='Sensors Data')


admin = Admin(app, name='Admin', index_view=HomeView(), template_mode='bootstrap4')
admin.add_view(views.SensorView(Sensor, db.session))


@app.route('/sensors')
def sensors():
    rows = db.session.query(Sensor.category, Sensor.loaded_at, Sensor.json_data) \
        .order_by(Sensor.loaded_at.desc()) \
        .limit(10)
    return jsonify([{**row} for row in rows])


scheduler = APScheduler(app=app)


@scheduler.task(trigger='interval', id="read_sensor", seconds=30)
def read_sensor():
    for sensor_creds in SensorsConfig.list():
        from_sensor = SensorReader(**sensor_creds).read()
        obj = Sensor(
            category=from_sensor.get('name'),
            json_data=json.dumps(from_sensor.get('data'))
        )
        with app.app_context():
            db.session.add(obj)
            db.session.commit()
            app.logger.debug(obj)
    #print("scheduler.task(trigger='interval', id='read_sensor', seconds=30)")


if __name__ == '__main__':
    #db.drop_all()
    with app.app_context():
        db.create_all()
    scheduler.start()
    # use_reloader=False - чтобы scheduler не выполнял дважды job
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    app.run(host='0.0.0.0', use_reloader=False, port=5000, debug=Config.DEBUG)
