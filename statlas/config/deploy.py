from base import *
from bundle_config import config
DATABASES = {
    "default": {
            'ENGINE': "django.db.backends.postgresql_psycopg2",
            'NAME': config['postgres']['database'],
            'USER': config['postgres']['username'],
            'PASSWORD': config['postgres']['password'],
            'HOST': config['postgres']['host'],
    },
}
EMAIL_HOST = 'localhost'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CACHE_BACKEND = 'file://' + IN_SITE_ROOT('../data/cache')

DEBUG = False

PRIVATE_DATA_ROOT = IN_SITE_ROOT('../data', 'private')
IN_PRIVATE_DATA_ROOT = functools.partial(os.path.join, PRIVATE_DATA_ROOT)

