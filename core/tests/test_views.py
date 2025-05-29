import pytest
from http import HTTPStatus
from django.test import SimpleTestCase


class RobotsTxtTests(SimpleTestCase):

    databases = '__all__'

    def test_get(self):
        response = self.client.get("/robots.txt")

        assert response.status_code == HTTPStatus.OK
        assert response["content-type"] == "text/plain"


@pytest.mark.parametrize(
    "icon",
    [
        "android-chrome-96x96.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
        "apple-touch-icon.png",
        "browserconfig.xml",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "favicon.ico",
        "mstile-150x150.png",
        "safari-pinned-tab.svg",
    ],
)
def test_favicon_response_ok(icon, client):
    resp = client.get("/" + icon)

    assert resp.status_code == 302
    assert resp["Cache-Control"] == "max-age=86400, immutable, public"
