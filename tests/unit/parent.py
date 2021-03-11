import os
import mock

from flask_testing import TestCase
from test.support import EnvironmentVarGuard


@mock.patch.dict(os.environ, {"PERSONALIZE_SRC_FILE": "../../app/personalize/rsvp_content.yaml"})
class ParentTest(TestCase):
    def create_app(self):
        self.env = EnvironmentVarGuard()
        self.env.set('DYNAMO_TABLE', 'test_table')
        self.env.set('AWS_REGION', 'us-west-1')
        self.env.set('PERSONALIZE_SRC_FILE', '../../app/personalize/rsvp_content.yaml')
        with self.env:
            from config import Config
            from tests import context
            app = context.app.create_app(Config)
            return app
