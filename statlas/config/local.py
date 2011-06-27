DATABASES = {
  'default': {
      'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
      'NAME': '',                      # Or path to database file if using sqlite3.
      'USER': '',                      # Not used with sqlite3.
      'PASSWORD': '',                  # Not used with sqlite3.
      'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
      'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
  }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CACHE_BACKEND = 'dummy://'

# Has no use locally
SEND_BROKEN_LINK_EMAILS=False

