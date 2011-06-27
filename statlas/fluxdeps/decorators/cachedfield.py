"""
    Some model methods generate output which takes a lot of time to compute,
    and which has to be used multiple times in a template. To this end, one can
    use the memoization-decorators described below.

    The smallest possible usecase is the following::

        def SomeModel(models.Model):
            @memoize
            def someComplexProperty(self):
                return 10**10 // A difficult computation here
                
    One can call `someComplexProperty` several times, the function body is 
    executed only once. There might be instances where the to-be memoized method has arguments,
    this also works.

    In case that one wants to memoize a raw query, use :func:`fluxbase.decorators.cachedfield.memoizeQuery`::

        @memoizeQuery(DISPLAY_NUMBER_LISTS)
        def SomeModel(models.Model):
            someRelation = models.ManyToManyField('someApp.SomeOtherModel')

        @memoizeQuery()
        def latestInitiatedLists(self):
            return self.someRelation_set.all()

    It is also possible to only store a limited amount of results, in this case,
    write::

        @memoizeQuery(SOME_ARBITRARY_BOUND)
"""

from functools import wraps

def memoize(method, processOutput = None):
    """Cache output of class methods in a dictionary depending on the input."""
    cacheName = '__%s_cached' % method.func_name

    @wraps(method)
    def wrapper(self, *args):
        funCache = getattr(self, cacheName, dict())

        if not args in funCache:
            result = method(self, *args)
            
            if not processOutput is None:
                result = processOutput(result)
            
            funCache[args] = result
            setattr(self, cacheName, funCache)
        else:
            result = funCache[args]
        
        return result

    return wrapper
    
def memoizeQuery(bound = None):
    """Cache output of class methods that returns a querySet"""
    makeList = list if bound is None else lambda querySet: list(querySet[:bound])
    
    return lambda method: memoize(method, processOutput = makeList)