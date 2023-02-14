import datetime as dt

from app import db


class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True, index=True)
    category = db.Column(db.String, nullable=False)
    json_data = db.Column(db.TEXT)
    loaded_at = db.Column(db.DateTime, default=dt.datetime.now)

    def __repr__(self):
        return f"Sensor(id={self.id}, category={self.category}, json_data={self.json_data}, loaded_at={self.loaded_at})"

        return self.render('admin/index.html', graphJSON=graphJSON, title='Sensors Data')