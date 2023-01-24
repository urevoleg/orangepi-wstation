import os
import datetime as dt
import json


from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from flask_apscheduler import APScheduler

from sensor_reader.reader import SensorReader

from config import Config


# init Flask
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, session_options={'autocommit': False})
admin = Admin(app, name='Admin', template_mode='bootstrap3')


class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True, index=True)
    category = db.Column(db.String, nullable=False)
    json_data = db.Column(db.TEXT)
    loaded_at = db.Column(db.DateTime, default=dt.datetime.now)


from views import SensorView
admin.add_view(SensorView(Sensor, db.session))


@app.route('/sensors')
def sensors():
    rows = db.session.query(Sensor.category, Sensor.loaded_at, Sensor.json_data) \
        .order_by(Sensor.loaded_at.desc()) \
        .limit(10)
    return jsonify([{**row} for row in rows])


scheduler = APScheduler()


@scheduler.task(trigger='interval', id="read_sensor", seconds=30)
def read_sensor():
    from_sensor = SensorReader(**{'host': '192.168.55.27', 'port': 80, 'path': 'sensors'}).read()
    obj = Sensor(
        category=from_sensor.get('name'),
        json_data=json.dumps(from_sensor.get('data'))
    )
    db.session.add(obj)
    db.session.commit()
    print("scheduler.task(trigger='interval', id='read_sensor', seconds=30)")


scheduler.init_app(app)
scheduler.start()


if __name__ == '__main__':
    #db.drop_all()
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)