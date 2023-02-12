import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from dotenv import load_dotenv
load_dotenv()


class Config(object):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True

    # ApsScheduler
    SCHEDULER_API_ENABLED = False
    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
    SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 2}}
    SCHEDULER_JOB_DEFAULTS = {"coalesce": False, "max_instances": 3}


class SensorsConfig:

    @staticmethod
    def list():
        return [
            {'host': '192.168.55.27', 'port': 80, 'path': 'sensors'},
            {'host': '192.168.55.124', 'port': 80, 'path': 'sensors'}
        ]