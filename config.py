import os


class Config(object):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    CSRF_ENABLED = True
