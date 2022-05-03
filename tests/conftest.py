import pytest
from prphish import create_app
import tempfile
import shutil
from os import path


@pytest.fixture()
def app():
    with tempfile.TemporaryDirectory() as tmpdirname:
        shutil.copy('./testingfiles/testdb.sqlite',
                    path.join(tmpdirname, 'db.sqlite'))
        app = create_app(instance_path=tmpdirname)
        app.config.update({
            "TESTING": True,
        })

        yield app

    # clean up / reset resources here


@ pytest.fixture()
def client(app):
    return app.test_client()


@ pytest.fixture()
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='admin@localhost', password='admin'):
        return self._client.post(
            '/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
