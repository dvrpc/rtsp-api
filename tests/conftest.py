import pytest
from fastapi.testclient import TestClient

import sys
sys.path.append("..")

from main import app


@pytest.fixture
def client():
    client = TestClient(app)
    return client
