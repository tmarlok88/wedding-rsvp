import os


class Config(object):
    LANGUAGES = ['en', 'hu']
    SECRET_KEY = os.environ.get('FLASK_SECRET')
    USE_RECAPTCHA_FOR_ADMIN = os.environ.get('USE_RECAPTCHA_FOR_ADMIN', False)
    USE_RECAPTCHA_FOR_GUEST = os.environ.get('USE_RECAPTCHA_FOR_GUEST', False)
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_OPTIONS = {'theme': 'white'}
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
