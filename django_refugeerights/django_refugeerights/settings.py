"""
Django settings for django_refugeerights project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = None

TEMPLATE_DEBUG = None

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    # admin
    'grappelli',
    'django.contrib.admin',
    # core
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # 3rd party
    'djcelery',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_hstore',
    'contentstore',
    # us
    'locationfinder',
    'metricsdownloader',
    'subscription',
    'snappyuploader',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_refugeerights.urls'

WSGI_APPLICATION = 'django_refugeerights.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default='postgis://postgres:@localhost/django_refugeerights'),
}

# django.contrib.gis.db.backends.postgis


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.core.context_processors.request",
# )

# Sentry configuration
RAVEN_CONFIG = {
    # DevOps will supply you with this.
    # 'dsn': 'http://public:secret@example.com/1',
}

# REST Framework conf defaults
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': None,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

# Celery configuration options
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

BROKER_URL = 'redis://localhost:6379/0'

from kombu import Exchange, Queue

CELERY_DEFAULT_QUEUE = 'django_refugeerights'
CELERY_QUEUES = (
    Queue('django_refugeerights',
          Exchange('django_refugeerights'),
          routing_key='django_refugeerights'),
)

CELERY_ALWAYS_EAGER = False

# Tell Celery where to find the tasks
CELERY_IMPORTS = (
    'locationfinder.tasks',
    'snappyuploader.tasks'
)

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

VUMI_GO_ACCOUNT_KEY = ""
VUMI_GO_CONVERSATION_KEY = ""
VUMI_GO_ACCOUNT_TOKEN = ""
LOCATION_RESPONSE_MAX_LENGTH = 320
LOCATION_NONE_FOUND = "Sorry, no locations found. Please try again later."
LOCATION_MAX_RESPONSES = 2
LOCATION_SEARCH_RADIUS = 10  # KM
METRIC_API_KEY = ""
METRIC_RECORDING_INTERVAL = "30d"

SNAPPY_BASE_URL = "https://app.besnappy.com/api/v1"
SNAPPY_ACCOUNT_ID = 12345
SNAPPY_API_KEY = "replaceme"
SNAPPY_MAILBOX_ID = 1
SNAPPY_EMAIL = "replaceme@example.org"
SNAPPY_EXTRAS = []


try:
    from local_settings import *   # flake8: noqa
except ImportError:
    pass
