from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m4g3l*ca&bpyhb5+oxpyd#035sz$6!-($+ywc)6le5g-3@qy^j"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"


try:
    from .local import *
except ImportError:
    pass
