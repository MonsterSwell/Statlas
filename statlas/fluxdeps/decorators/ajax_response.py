"""
    The AjaxResponse object is a wrapper fot he HttpResponse object. It will
    translate all the data send to the view, into a JSON-format (using simpe
    JSON).

    This method is part of the Django-Annoying library
    https://bitbucket.org/offline/django-annoying
"""

from django.http import HttpResponse
from django.utils import simplejson

class JsonResponse(HttpResponse):
    """HttpResponse descendant, which return response with ``application/json`` mimetype."""
    def __init__(self, data):
        super(JsonResponse, self).__init__(
                content     = simplejson.dumps(data)
            ,   mimetype    ='application/json'
        )



def ajax_request(func):
    """
    Wraps to JSON-response.
    
    Wraps method to return a :class:`JsonResponse` with this `dict` as content in case
    the method returns a `dict`. Example usage::
    
        @ajax_request
        def my_view(request):
            news = News.objects.all().values_list('title', flat = True)
            return { 'news_titles': list(news) }
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)

        return JsonResponse(response) if isinstance(response, dict) else response
        
    return wrapper
