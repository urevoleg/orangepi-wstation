import datetime as dt
import json

from statistics import mean, StatisticsError

from app import app, db, models


def row_handler(row):
    return int(json.loads(row.json_data).get('p')) / 10.0


def formatted_forecast(prev_p, cur_p):
    speed = round(cur_p - prev_p, 3)
    speed_kpa = round(speed * 1 / 7.50062, 3)

    if speed_kpa > 0.25:
        msg = {
            'speed': speed,
            'speed_kpa': speed_kpa,
            'long': "Quickly rising High Pressure System, not stable",
            'short': 'QR'
        }
    elif speed_kpa > 0.05 and speed_kpa <= 0.25:
        msg = {
            'speed': speed,
            'speed_kpa': speed_kpa,
            'long': "Slowly rising High Pressure System, stable good weather",
            'short': 'SR'
        }
    elif speed_kpa > -0.05 and speed_kpa <= 0.05:
        msg = {
            'speed': speed,
            'speed_kpa': speed_kpa,
            'long': "Stable weather condition",
            'short': 'ST'
        }
    elif speed_kpa > -0.25 and speed_kpa <= -0.05:
        msg = {
            'speed': speed,
            'speed_kpa': speed_kpa,
            'long': "Slowly falling Low Pressure System, stable rainy weather",
            'short': 'SF'
        }
    else:
        msg = {
            'speed': speed,
            'speed_kpa': speed_kpa,
            'long': "Quickly falling Low Pressure, Thunderstorm, not stable",
            'short': 'QF'
        }

    return msg


def get_forecast():

    is_no_prev_data = db.session.query(True)\
        .order_by(models.Sensor.loaded_at.desc()) \
        .filter(models.Sensor.category == 'weather-out') \
        .filter(models.Sensor.loaded_at >= dt.datetime.now() - dt.timedelta(hours=1, minutes=5),
                models.Sensor.loaded_at < dt.datetime.now() - dt.timedelta(hours=1)).first()

    last_hour = db.session.query(models.Sensor.category, models.Sensor.loaded_at, models.Sensor.json_data) \
        .order_by(models.Sensor.loaded_at.desc()) \
        .filter(models.Sensor.category == 'weather-out') \
        .filter(models.Sensor.loaded_at >= dt.datetime.now() - dt.timedelta(hours=1, minutes=5),
                models.Sensor.loaded_at < dt.datetime.now() - dt.timedelta(hours=1))

    current_hour = db.session.query(models.Sensor.category, models.Sensor.loaded_at, models.Sensor.json_data) \
        .order_by(models.Sensor.loaded_at.desc()) \
        .filter(models.Sensor.category == 'weather-out') \
        .filter(models.Sensor.loaded_at >= dt.datetime.now() - dt.timedelta(minutes=5))

    try:
        return formatted_forecast(mean(row_handler(row) for row in last_hour), mean(row_handler(row) for row in current_hour))
    except StatisticsError as e:
        app.logger.debug(is_no_prev_data)
        #TODO baseline
        # Если каких-то данных нет, например, текущих или час назад, то надо что-то делать
        # например, можно взять среднее за последние 3\6\12 (по выбору) часов
        return {
            'speed': 0.0,
            'speed_kpa': 0.0,
            'long': "Undefined weather condition",
            'short': 'UF',
            'error': str(e)
        }


if __name__ == '__main__':
    with app.app_context():
        app.logger.debug(get_forecast())