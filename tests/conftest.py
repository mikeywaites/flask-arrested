import pytest

from flask import Flask
from arrested import ArrestedAPI


@pytest.yield_fixture
def app():
    app = Flask(__name__)
    with app.test_request_context():
        yield app


@pytest.fixture
def api_v1(app):
    api_v1 = ArrestedAPI(app, url_prefix='/v1')
    return api_v1


@pytest.yield_fixture
def client(app):
    """A Flask test client. An instance of :class:`flask.testing.TestClient`
    by default.
    """
    with app.test_client() as client:
        yield client
