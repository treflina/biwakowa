import pytest


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
