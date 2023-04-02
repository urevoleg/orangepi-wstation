from app import app, db, models
from flask import jsonify


@app.route('/sensors')
def sensors():
    categories = db.session.query(models.Sensor.category).distinct()
    data = [{**db.session.query(models.Sensor.category, models.Sensor.loaded_at, models.Sensor.json_data) \
        .order_by(models.Sensor.loaded_at.desc())\
        .filter(models.Sensor.category==category)\
        .first()} for category in categories]

    return jsonify(data)