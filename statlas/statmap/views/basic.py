from fluxdeps.decorators import render_to
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db.models import Q
from django.http import Http404
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required


import json

from statmap.forms import MappingForm, FilterMapsForm
from statmap.models import DataSet
from statmap.models import FavoriteDataSet
from accounts.models import LogEntry


from helper import get_data_set, get_public_data_set_querset

@login_required
@render_to('statmap/create.html')
def create(request):
    data = request.POST if request.method=='POST' else None

    form    = MappingForm(data=data)

    #if form.is_valid():
    #    pass#form.save()
    return render_to_response('statmap/create.html',
        {'form': form}, context_instance = RequestContext(request))
    #return { 'form': form }

def save(request):
    """
        Requires a post variabel `data`

        Returns a JSON file in the following format:

        .. code ::
            {
                'id': 'the id of the dataset',
                'status': 'success|error',
                'message': 'textual repr. of error / form errors dump',
            }

        `message` and `error_code` will be left out if there
        are no errors.
    """
    if request.user.is_authenticated():
        form = MappingForm(data=request.POST, user=request.user)
        if form.is_valid():
            data_set = form.save()

            json_response = {
                'status': 'success',
                'dataset': data_set.slug,

            }

            json_response['data_sets'] = list(DataSet.objects\
                           .filter(get_public_data_set_querset(request.user))
                           .filter(regionset=data_set.regionset)\
                           .values('title', 'slug'))
        else:
            json_response = {
                'status': 'error',
                'errors': form.errors,
            }
    else:
        json_response = {
            'status': 'error',
            'messages': "You are not signed in",
        }




    response = HttpResponse()
    json.dump(json_response, response)
    return response


def explore(request, *args, **kwargs):
    """
      Show a list of maps. If the user has not used the
      filter options we shall display the last recent maps,
      otherwise we use the filtered maps.
    """
    data = request.POST if request.method=='POST' else None
    form    = FilterMapsForm(data=data)

    qs = DataSet.objects\
                .filter(get_public_data_set_querset(request.user))\
                .order_by('-date_created')

    if form.is_valid() and form.is_active():
        maps = form.filtered_results(qs)
    else:
        maps = qs.order_by('-date_created')

    kwargs.update( {
        'paginate_by': 16,
        'template_name': 'statmap/explore.html',
        'template_object_name': 'map',
    })

    return object_list(request, extra_context={'form': form }, queryset=maps, *args, **kwargs)


@render_to('statmap/mapdetail.html')
def mapdetail(request, slug):
    """
      Select the dataset requested. If the user is not authenticated,
      choose only from the public maps. Otherwise also search the
      users own maps

      .. TODO ::
        Wout: what is a user opens his own map but is not authenticated.
        For now the user gets presented a 404, but maybe its better
        to tell him the map exists but the user has not got
        permission to view it.

    """
    data_set = get_data_set(request.user, slug, allow_empty=False)
    data_set.update_recently_viewed_by(request.user)

    favorited_by_user = data_set.is_favorited_by(request.user)


    return {'map': data_set,
            'favorited_by_user': favorited_by_user}

@render_to('statmap/embed.html')
def embed(request, slug):
    """
      Select the dataset requested. If the user is not authenticated,
      choose only from the public maps. Otherwise also search the
      users own maps

      .. TODO ::
        Wout: what is a user opens his own map but is not authenticated.
        For now the user gets presented a 404, but maybe its better
        to tell him the map exists but the user has not got
        permission to view it.

    """
    data_set = get_data_set(request.user, slug, allow_empty=False)

    return {'map': data_set}

def favorite(request, slug):
    """
        Favorite is called using JS and add the
        given DataSet to the users Favorites list.

        The response will be a JSON object

        {
            'status': 'success|error',
            'message': 'textual repr. of error',
        }

        or a 404 if the data_set does not exist
    """
    if not request.user.is_authenticated():
        json_response = { 'status': 'error', 'message': 'You are not signed in'}
    else:
        data_set = get_data_set(request.user, slug, allow_empty=False)

        FavoriteDataSet.objects.get_or_create(dataset=data_set,
                                              user=request.user)

        # User cannot favorite twice, so no need to update the
        # time record

        json_response = { 'status': 'success', 'message': ''}


    response = HttpResponse()
    json.dump(json_response, response)
    return response

def unfavorite(request, slug):
    from statmap.models import FavoriteDataSet
    """
        Unfavorite is called using JS and removes the
        given DataSet to the users Favorites list.

        The response will be a JSON object

        {
            'status': 'success|error',
            'message': 'textual repr. of error',
        }

        or a 404 if the data_set does not exist.

        If the user hasnt favorited this element just
        fail silently
    """
    if not request.user.is_authenticated():
        json_response = { 'status': 'error', 'message': 'User is not signed in'}
    else:
        data_set = get_data_set(request.user, slug, allow_empty=False)

        FavoriteDataSet.objects.filter(dataset=data_set,
                                       user=request.user)\
                               .delete()
        json_response = { 'status': 'success', 'message': ''}


    response = HttpResponse()
    json.dump(json_response, response)
    return response


@render_to('about.html')
def about(request):
  return {}

