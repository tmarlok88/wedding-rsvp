import os


class Config(object):
    LANGUAGES = ['en', 'hu']
    SECRET_KEY = os.environ.get('FLASK_SECRET')
