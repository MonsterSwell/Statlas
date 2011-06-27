from django.http import HttpResponse, Http404
import json
from django.db.models import Q

from statmap.models import Region, RegionSet, DataSet, DataValue

from helper import get_data_set, get_public_data_set_querset


def region_set_list(request):
    """
        Methods return a JSON list for the current QuerySet in the
        following format:

        .. code-block:: js
            {
                'regionsets':
                [
                    { 'slug': '...', 'value': '...'},
                    { 'slug': '...', 'value': '..' },
                    ..
                ]
            }
    """
    region_sets = RegionSet.visible_objects.all().values('title', 'slug')

    response = HttpResponse(mimetype='application/json')
    json.dump(list(region_sets), response)

    return response

def region_set_geo(request, region_set_slug):
    """
        Method returns a GeoJSON file as specified in
        :link:`http://geojson.org/geojson-spec.html`.

        The `properties` attribute of each `feature` will
        have a `cityName` and a `citySlug` that corresponds
        with the display name and the slug as it is known
        to the database system.

        .. todo ::
            This method takes a lot of time because we
            have to convert plain/text geoJson to
            JSON object and back again to insert the
            coordinates.

            This can be solved by applying some caching
            or by finding a faster way to produce the
            JSON file.

            If we choose to cache, we must make sure
            that we destroy cache when we update the
            regions.
    """
    try:
        region_set = RegionSet.visible_objects.get(slug=region_set_slug)
    except RegionSet.DoesNotExist:
        raise Http404('Region set does not exsist')

    response = HttpResponse(region_set.json, mimetype='application/json')
    return response

def data_set_list(request, region_set_slug):
    """
        Methods return a JSON list for the available datasets for this
        region set.

        .. code-block:: js
            {
                'dataset':
                [
                    { 'slug': '...', 'value': '...'},
                    { 'slug': '...', 'value': '.. },
                    ..
                ]
            }
    """
    try:
        region_set = RegionSet.visible_objects.get(slug=region_set_slug)
    except RegionSet.DoesNotExist:
        raise Http404('Region set does not exsist')    
    
    q = get_public_data_set_querset(request.user)

    data_sets = region_set.data_sets\
                           .filter(q) \
                           .values('title', 'slug')
                       
    
    response = HttpResponse(mimetype='application/json')
    json.dump(list(data_sets), response)

    return response

def data_set(request, region_set_slug, data_set_slug):
    """
        Returns a JSON file with some keys for the Meta
        data and a list with key/value pairs.

        .. code-block:: js
            {
              values:
                citySlug: value,
                citySlug: value,
                citySlug: value,
                citySlug: value,
                ...,
              ],
              meta: {
                title: value,
                dataset: value,
                public: value,
                description: value,
                author: value,
                zoom: value,
                lat: value,
                lng: value,
                region: value
              }
            };


        `empty.json` returns a list with all values set to "" and
        `slug` set to 'empty'.
    """
    data_set = get_data_set(request.user, data_set_slug, region_set_slug)
    
    values = {}
    for k,v in data_set.data_values.by_region(data_set.regionset).items():
        values[k] = v.value
    
    data_set_return = \
    {
        'values': values,
        'meta':
        {
            'title': data_set.title,
            'dataset': data_set.slug,
            'public': data_set.public,
            'description': data_set.description,
            'author': 'Not implemented yet',
            'zoom': data_set.zoom,
            'latitude': data_set.latitude,
            'longitude': data_set.longitude,
            'regionset': region_set_slug
        }
    }

    response = HttpResponse(mimetype='application/json')
    json.dump(data_set_return, response, indent=4)    # .. todo :: remove indent
    return response

