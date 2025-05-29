import json
import os

from flask_apscheduler import APScheduler

from .sensor_reader.reader import SensorReader
from .narodmon_sender.sender import Sender

from app import app, db
from app import models, SensorsConfig


logging.basicConfig(level=logging.DEBUG,
                format="⏰ %(asctime)s - 💎 %(levelname)s - %(filename)s - %(funcName)s:%(lineno)s - 🧾 %(message)s")
logger = logging.getLogger(__name__)


scheduler = APScheduler(app=app)


@scheduler.task(trigger='interval', id="read_sensor", seconds=30)
def read_sensor():
    for sensor_creds in SensorsConfig.list():
        try:
            from_sensor = SensorReader(**sensor_creds).read()
            obj = models.Sensor(
                category=from_sensor.get('name'),
                json_data=json.dumps(from_sensor.get('data'))
            )
            with app.app_context():
                db.session.add(obj)
                db.session.commit()
                app.logger.debug(obj)
        except Exception as e:
            logger.error(f'Error: {e} occured while executing for sensor: {sensor_creds}')


@scheduler.task(trigger='interval', id="narodmon_send", minutes=5)
def narodmon_send():
    with app.app_context():
        with db.engine.connect() as conn:
            stmt = """with out_ as (select 1 AS KEY,
                                            round(avg(cast(json_data::json->> 'l' as numeric)), 0) as l, 
                                            round(avg(0.01 * cast(json_data::json->> 't' as numeric)), 2) as t_out, 
                                            round(avg(0.1 * cast(json_data::json->> 'p' as numeric)), 1) as p
                                    from sensors
                                    where loaded_at > timezone('utc-3', now()) - interval '5min'
                                    and category = 'weather-out'),
                        in_ AS (select 1 AS KEY,
                                            round(avg(cast(json_data::json->> 'gas' as numeric)), 0) as gas, 
                                            round(avg(0.01 * cast(json_data::json->> 't' as numeric)), 2) as t_in 
                                    from sensors
                                    where loaded_at > timezone('utc-3', now()) - interval '5min'
                                    and category = 'weather-in')
                        select *
                        from out_
                        JOIN in_
                        USING (key);"""
            res = conn.execute(stmt)

            data = {'ID': os.getenv('NARODMON_DEVICE_MAC')}
            for row in res.fetchall():
                for k, v in row.items():
                    if k != 'key':
                        data[Sender._name_sensor_mappings(k)] = float(str(v))
            app.logger.debug(data)
            sender = Sender(host=os.getenv('NARODMON_HOST'),
                            port=os.getenv('NARODMON_PORT'),
                            post_uri=os.getenv('NARODMON_POST_URI'))
            response = sender.send(data=data)
            app.logger.debug((response, response.headers))


if __name__ == '__main__':
    narodmon_send()
