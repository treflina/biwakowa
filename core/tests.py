from http import HTTPStatus

from django.test import SimpleTestCase


class FaviconFileTests(SimpleTestCase):
    databases = '__all__'

    def test_get(self):
        names = [
            "android-chrome-192x192.png",
            "android-chrome-512x512.png",
            "apple-touch-icon.png",
            "browserconfig.xml",
            "favicon-16x16.png",
            "favicon-32x32.png",
            "favicon.ico",
            "mstile-150x150.png",
            "safari-pinned-tab.svg",
            "browserconfig.xml"
        ]

        for name in names:
            with self.subTest(name):
                response = self.client.get(f"/{name}")

                self.assertIn(response.status_code, [HTTPStatus.OK, HTTPStatus.FOUND])
                self.assertEqual(
                    response["Cache-Control"],
                    "max-age=86400, immutable, public",
                )
                self.assertGreater(len(response.url), 0)
