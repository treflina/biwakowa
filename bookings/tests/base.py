from faker import Faker

faker = Faker()


def anonymous_user_redirected_to_login(client, url, login_url):
    resp = client.get(url)

    assert resp.status_code == 302
    assert str(login_url) in resp.url
