import datetime as dt
import json

from app import app, db, models, forecast
from flask import jsonify, request


@app.route('/sensors')
def sensors():
    categories = db.session.query(models.Sensor.category).distinct()
    data = [{**db.session.query(models.Sensor.category, models.Sensor.loaded_at, models.Sensor.json_data) \
        .order_by(models.Sensor.loaded_at.desc())\
        .filter(models.Sensor.category==category.category)\
        .first()} for category in categories]

    #TODO надо преобразовать json_load в dict (сейчас строка)
    for res in data:
        if res['category'] == 'weather-out':
            res['forecast'] = forecast.get_forecast()

    return jsonify(data)


@app.route('/debug')
def debug():
    with db.engine.connect() as conn:
        stmt = """with out_ as (select 1 AS KEY,
                                        max(loaded_at) as out_loaded_at,
                                        round(avg(cast(json_data::json->> 'l' as numeric)), 0) as l, 
                                        round(avg(0.01 * cast(json_data::json->> 't' as numeric)), 2) as t_out, 
                                        round(avg(0.1 * cast(json_data::json->> 'p' as numeric)), 1) as p
                                from sensors
                                where loaded_at > timezone('utc-3', now()) - interval '5min'
                                and category = 'weather-out'),
                    in_ AS (select 1 AS KEY,
                                        max(loaded_at) as out_loaded_at,
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

    return jsonify([{**row} for row in res.fetchall()])


@app.route('/weather/<place>')
def get_data(place: str='out'):
    app.logger.debug(request)
    app.logger.debug(place)
    request_data = json.loads(request.json)
    return jsonify({
        'dt': dt.datetime.now(),
        'place': place
    })