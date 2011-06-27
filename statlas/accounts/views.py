from fluxdeps.decorators import render_to
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import LogEntry

@render_to('accounts/public_profile.html')
def profile(request, username):
    if request.user.is_authenticated() and request.user.twitter_profile.screen_name==username:
        return own_profile(request)


    user = get_object_or_404(User, twitter_profile__screen_name=username)

    public_maps = user.data_sets.filter(public=True)
    favorite         = user.favorite_datasets.order_by('title')


    return { 'user': user,
             'public_maps': public_maps,
             'favorite': favorite }

@login_required
@render_to('accounts/private_profile.html')
def own_profile(request):
    user = request.user

    recently_changed = user.data_sets.order_by('-date_changed')
    recently_viewed  = user.recently_viewed_datasets.order_by('-recently_viewed_data_set__date_changed')
    favorite         = user.favorite_datasets.order_by('title')
    history          = LogEntry.objects.filter(user__id__exact=user.id)\
                                       .select_related('content_type', 'user')


    return {'user': user,
            'recently_changed': recently_changed,
            'recently_viewed': recently_viewed,
            'favorite': favorite,
            'history': history}

#    if username==None:
#        if request.user.is_authenticated():
#            return HttpResponseRedirect(reverse('accounts:profile', {'username': request.user.username}))
#        else:
#            raise Http404("No username specified and not logged in")
#
#
#    user = get_object_or_404(user=username)
#
#    return {'user': user}

