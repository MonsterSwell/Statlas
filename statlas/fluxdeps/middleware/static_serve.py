"""
    The development server does not automatically serve up static files. This is
    very inconvenient, the middleware :class:`StaticServe` solves this. Simply add::

        MIDDLEWARE_CLASSES.append('fluxbase.staticserve.middleware.StaticServe')

    to your configuration file, and you're set.

    .. note::
        The :class:`StaticServe` only serves up files in case that `DEBUG`
        is set to `True`. In a production environment, this middleware is very
        inappropriate.

    This class is based on the Django-Annoying version of StaticServe
    https://bitbucket.org/offline/django-annoying/
"""

import re
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from django.views.static import serve

class StaticServe(object):
    """Django middleware for serving static files"""
    regex = re.compile(r'^%s(?P<path>.*)$' % settings.MEDIA_URL)

    def __init__(self):
        # Make sure that the middleware is only used when debug is set to True
        if not settings.DEBUG:
            raise MiddlewareNotUsed()

    def process_request(self, request):
        if settings.DEBUG:
            match = self.regex.match(request.path)
            
            if match:
                return serve(request, match.group('path'), settings.MEDIA_ROOT)
