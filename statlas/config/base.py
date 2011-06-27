import socket
import os.path, functools
from fluxdeps.helpers import get_secret_key

DEBUG = True


"""
  Some helper functions for making life easy
"""
# Helper for translations
# http://docs.djangoproject.com/en/dev/ref/settings/#languages
gettext = lambda s: s

# The actual site root and a helper function to point to a folder in siteroot
SITE_ROOT = os.path.realpath(os.path.dirname(__file__)+'/../')
IN_SITE_ROOT = functools.partial(os.path.join, SITE_ROOT)

"""
  Settings
"""

SITE_ID=1

# List of people to notify on server error
# http://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
)

# List of people to notify on broken link error
# http://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS=True

# Local time zone
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# http://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
# http://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en'

# Use of I18N (custom language) and L18N (dates)
# http://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
# http://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_I18N = True
USE_L10N = True

USE_THOUSAND_SEPARATOR = True

# Link to default and admin media.
# ADMIN_MEDIA_PREFIX mag niet gelijk zijn aan MEDIA_ROOT
# http://docs.djangoproject.com/en/dev/ref/settings/#admin-media-prefix
MEDIA_ROOT = IN_SITE_ROOT('media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin/media/'

PRIVATE_DATA_ROOT = IN_SITE_ROOT('data', 'private')
IN_PRIVATE_DATA_ROOT = functools.partial(os.path.join, PRIVATE_DATA_ROOT)

SECRET_KEY = get_secret_key()

# Debug Toolbar
# https://github.com/robhudson/django-debug-toolbar
#INTERNAL_IPS = ('127.0.0.1',)

# http://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'fluxdeps.middleware.StaticServe',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'fluxdeps.middleware.OmitWWW',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
  IN_SITE_ROOT('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.admin',
    'django.contrib.humanize',

    'fluxdeps.default',
    'debug_toolbar',

    'socialregistration',

    'statmap',
    'accounts',
)

# No WWW
PREPEND_WWW = False

"""
OAUTH
"""

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'

AUTHENTICATION_BACKENDS = (
                           'django.contrib.auth.backends.ModelBackend',
                           'socialregistration.auth.TwitterAuth',
                           )

SOCIALREGISTRATION_GENERATE_USERNAME = True

"""
URL2PNG
"""
URL2PNG_APIKEY = ''
URL2PNG_SECRET = ''
URL2PNG_BOUNDS = "500x500"

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

