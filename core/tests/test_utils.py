import pytest

from django.core import mail

from ..utils.log import CustomAdminEmailHandler


@pytest.mark.django_db
def test_custom_email_handler():
    handler = CustomAdminEmailHandler()
    handler.send_mail("subj", "msg")

    assert len(mail.outbox) == 1
