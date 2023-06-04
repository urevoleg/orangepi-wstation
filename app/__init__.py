import logging
from logging import StreamHandler

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from app.config import Config, SensorsConfig


# init Flask
app = Flask(__name__)
app.config.from_object(Config)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_sqla = logging.getLogger('sqlalchemy.engine')
logger_sqla.setLevel(logging.DEBUG)
handler = StreamHandler()
handler.setFormatter(fmt=formatter)
logger_sqla.addHandler(handler)

logger = logging.getLogger('wstation')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

app.logger = logger

db = SQLAlchemy(app, session_options={'autocommit': False})

from app import models, views, routes, tasks, forecast

admin = Admin(app, name='Admin', index_view=views.HomeView(), template_mode='bootstrap4')
admin.add_view(views.SensorView(models.Sensor, db.session))


def init_db():
    with app.app_context():
        db.create_all()


init_db()

tasks.scheduler.start()


if __name__ == '__main__':
    #db.drop_all()

    # use_reloader=False - чтобы scheduler не выполнял дважды job
    # https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
    # https://github.com/viniciuschiele/flask-apscheduler/issues/139
    app.run(host='0.0.0.0', use_reloader=False, port=5000, debug=Config.DEBUG)
