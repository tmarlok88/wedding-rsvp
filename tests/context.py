import os
import sys
from unittest import mock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

with mock.patch.dict(os.environ, {"AWS_REGION": "us-west-1", "DYNAMO_TABLE": "fake-table"}):
    import app