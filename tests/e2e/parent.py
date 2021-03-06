import os
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from test.support import EnvironmentVarGuard
import threading
import time

from moto.server import create_backend_app
from tests.guest_helper import clear_all_guests

MAX_WAIT = 5


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn


class E2ETest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.env = EnvironmentVarGuard()

        if os.getenv("IS_LOCAL", True):
            cls.env.set('DYNAMO_TABLE', 'test_table')
            cls.env.set('AWS_REGION', 'us-west-1')
            cls.env.set('AWS_ENDPOINT_URL', 'http://localhost:7012')
            cls.env.set('AWS_ACCESS_KEY_ID', 'testing')
            cls.env.set('AWS_SECRET_ACCESS_KEY', 'testing')
            cls.env.set('AWS_SECURITY_TOKEN', 'testing')
            cls.env.set('AWS_SESSION_TOKEN', 'testing')
            cls.moto_app = create_backend_app("dynamodb2")
            cls.moto_thread = threading.Thread(target=cls.moto_app.run, args=("localhost", 7012),
                                               kwargs={"use_reloader": False})
            cls.moto_thread.setDaemon(True)
            cls.moto_thread.start()

    def setUp(self) -> None:
        browser = os.getenv("E2E_BROWSER", "firefox")
        if browser == "firefox":
            self.browser = webdriver.Firefox()
        if browser == "chrome":
            self.browser = webdriver.Chrome()
        if browser == "edge":
            self.browser = webdriver.Edge()
        self.addCleanup(self.browser.quit)

    def tearDown(self) -> None:
        clear_all_guests()

    def create_app(self):
        with self.env:
            from config import Config
            from tests import context
            app = context.app.create_app(Config)
            app.config['LIVESERVER_PORT'] = 0
            app.config['ADMIN_PASSWORD_HASH'] = "pbkdf2:sha256:150000$nC4kA7sN$89c5edf694d455af7f1ff29ac46c77bddfd0069e8e806a29037ca33ee488070f"        # password
            from app.model.Guest import Guest
            Guest.create_table()
            return app

    @wait
    def wait_for(self, fn):
        return fn()
