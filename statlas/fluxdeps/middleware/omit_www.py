"""
    Having www in front of your domain name is ugly. This piece of middleware
    prevents that from happening. In order to activate it, add the following to
    the django configuration file::

        PREPEND_WWW = False
        MIDDLEWARE_CLASSES.append('fluxdeps.middleware.OmitWWW')

    In a bit more detail, make sure that you add
    `fluxdeps.middleware.OmitWWW` to the list of middleware,
    and switch `PREPEND_WWW` to False. PREPEND_WWW is False by default

    .. warning::
        This method has changed during introduction to baseproject. It used
        settings.OMIT_WWW=True instead of settings.PREPEND_WWW=False. OMIT/PREPEND
        were opposites. Sleepy settings could create an infinite loop. Therefore
        only PREPEND is used.

    .. moduleauthor:: Jeroen Goudsmit <jeroen@fluxility.com>
    .. moduleauthor:: Wouter Klein Heerenbrink <wouter@fluxility.com>
"""


from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils.http import urlquote

class OmitWWW(object):
    """
        Redirect requests to hosts with 'www.' in front of them to the same host
        with the 'www.' prefix dropped.
    """        
    def process_request(self, request):
        host = request.get_host()
        path = request.path

        if (not getattr(settings, 'PREPEND_WWW', False)) and host and host.startswith('www.'):
            host = host[4:]

            url = '%s://%s%s' % \
                (
                        'https' if request.is_secure() else 'http'
                    ,   host
                    ,   urlquote(path)
                )

            if request.GET:
                qs = request.META['QUERY_STRING']
                if len(qs) > 0:
                    url += '?' + qs

            return HttpResponsePermanentRedirect(url)
