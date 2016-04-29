from django_refugeerights.settings import *  # flake8: noqa

DATABASES = {
    'default': dj_database_url.config(
        default='postgis://postgres:@localhost/django_refugeerights'),
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'TESTSEKRET'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

LOCATION_SEARCH_RADIUS = 20  # KM
LOCATION_MAX_RESPONSES = 2

VUMI_GO_ACCOUNT_KEY = 'acc-key'
VUMI_GO_CONVERSATION_KEY = 'conv-key'
VUMI_GO_ACCOUNT_TOKEN = 'conv-token'

SNAPPY_ACCOUNT_ID = 12345
SNAPPY_API_KEY = "testkey"


try:
    from local_settings import *   # flake8: noqa
except ImportError:
    pass