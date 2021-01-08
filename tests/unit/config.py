from werkzeug.security import generate_password_hash

class Config(object):
    LANGUAGES = ['en', 'hu']
    TESTING = True
    USE_RECAPTCHA_FOR_ADMIN = False
    USE_RECAPTCHA_FOR_GUEST = False
    SECRET_KEY = "testingsecret"
    WTF_CSRF_ENABLED = False

