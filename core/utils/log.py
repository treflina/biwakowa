from django.conf import settings
from django.core import mail
from django.utils.log import AdminEmailHandler


class CustomAdminEmailHandler(AdminEmailHandler):
    """Custom email handler without vulnerable data sending"""

    def send_mail(self, subject, message, *args, **kwargs):
        site_name = settings.WAGTAIL_SITE_NAME
        msg = f"Error in {site_name}"
        mail.mail_admins(
            subject, message=msg, *args, connection=self.connection(), **kwargs
        )
