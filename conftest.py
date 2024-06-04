import pytest
from marhaba_app.app import MarhabaApp


@pytest.fixture
def app():
    return MarhabaApp()


@pytest.fixture
def test_client(app):
    return app.test_session()
