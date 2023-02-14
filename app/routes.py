from app import app, db, models
from flask import jsonify


@app.route('/sensors')
def sensors():
    rows = db.session.query(models.Sensor.category, models.Sensor.loaded_at, models.Sensor.json_data) \
        .order_by(models.Sensor.loaded_at.desc()) \
        .limit(10)
    return jsonify([{**row} for row in rows])