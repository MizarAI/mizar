import os

import pytest
import requests_mock

from mizar.api import Mizar
from mizar.api import MizarAPIException


@pytest.fixture()
def client():
    client = Mizar("api_key")
    return client


def test_missing_key():
    os.environ["MIZAR_API_KEY"] = ""
    with pytest.raises(ValueError):
        Mizar()


def test_not_allowed_key():
    with pytest.raises(ValueError):
        Mizar("api_key", scheme="not_allowed_scheme")


def test_key_from_environ():
    os.environ["MIZAR_API_KEY"] = "test"
    Mizar()


def test_ping_api_exception(client):
    with pytest.raises(MizarAPIException):
        with requests_mock.mock() as m:
            m.get(
                "https://api.mizar.ai/v1/ping",
                json={"message": "API exception"},
                status_code=400,
            )
            client.ping()


def test_ping_working(client):
    with requests_mock.mock() as m:
        m.get(
            "https://api.mizar.ai/v1/ping",
            json={"message": "pong"},
            status_code=200,
        )
        client.ping()
