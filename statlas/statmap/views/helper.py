from django.http import Http404
from django.db.models import Q
from statmap.models import RegionSet, DataSet


def get_public_data_set_querset(user):
    """
        Return a QuerySet to filter the list of `DataSet`s by
        the property `public` or `owned by user`.
    """
    if not user.is_authenticated():
        q = Q(public=True)
    else:
        q = Q(public=True) | Q(author=user)
        
    return q

def get_data_set(user, data_set_slug, region_set_slug=None, allow_empty=True):
    """
        Get a DataSet that is `public` or owned by the user.
        
        :param user:              The `User`; can be `AnonymousUser`
        :param data_set_slug:     The slug of the datase
        :param region_set_slug:  `Optional`
    
        :returns:                The requested `DataSet` if available
        :raises:                 Http404
    """
    try:
        q = get_public_data_set_querset(user)

        data_set = DataSet.objects

        if region_set_slug:
            data_set = data_set.filter(regionset__slug = region_set_slug)
            
        data_set = data_set.get( \
                            q, \
                            slug            = data_set_slug)
        

        
    except DataSet.DoesNotExist:
        try:
            if data_set_slug == 'empty' and region_set_slug and allow_empty:
                region_set = RegionSet.objects.get(slug=region_set_slug)
                data_set = DataSet(slug="empty", regionset=region_set)
            else:
                raise DataSet.DoesNotExist
        except DataSet.DoesNotExist, RegionSet.DoesNotExist:
            raise Http404
        
    return data_set