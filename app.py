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


import views


admin = Admin(app, name='Admin', template_mode='bootstrap4')
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


with app.app_context():
    db.create_all()
scheduler.start()


if __name__ == '__main__':

    # use_reloader=False - чтобы scheduler не выполнял дважды job
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    app.run(host='0.0.0.0', use_reloader=False, port=5000, debug=Config.DEBUG)
