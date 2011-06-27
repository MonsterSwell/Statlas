import uuid

from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.db import IntegrityError


from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout as auth_logout


from socialregistration.models import TwitterProfile
from socialregistration import signals 


def _get_next(request):
    """
    Returns a url to redirect to after the login
    """
    if 'next' in request.session:
        next = request.session['next']
        del request.session['next']
        return next
    elif 'next' in request.GET:
        return request.GET.get('next')
    elif 'next' in request.POST:
        return request.POST.get('next')
    else:
        return '/'

def _login(request, user, profile, client):
    login(request, user)
    signals.login.send(sender = profile.__class__, 
                                  user = user,
                                  profile = profile, 
                                  client = client)

def _connect(user, profile, client):
    signals.connect.send(sender = profile.__class__,
                                    user = user,
                                    profile = profile,
                                    client = client)

def logout(request, redirect_url=None):
    """
    Logs the user out of django. This is only a wrapper around
    django.contrib.auth.logout. Logging users out of Facebook for instance
    should be done like described in the developer wiki on facebook.
    http://wiki.developers.facebook.com/index.php/Connect/Authorization_Websites#Logging_Out_Users
    """
    auth_logout(request)

    url = redirect_url or getattr(settings, 'LOGOUT_REDIRECT_URL', '/')

    return HttpResponseRedirect(url)

def create_user(usernames=[]):
    usernames.reverse()
    
    while usernames:
        try:
            user = User(username=usernames.pop().lower())
            user.save()
            break;
        except IntegrityError:  # Username exists
            user = None
            continue
          
    if not user: # Given usernames were all not unique
        user = User(username=str(uuid.uuid4())[:30])
        user.save()
      
    return user

def twitter(request, account_inactive_template='socialregistration/account_inactive.html',
    extra_context=dict(), client_class=None):
    """
    Actually setup/login an account relating to a twitter user after the oauth
    process is finished successfully
    """
    client = client_class(
        request, settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET_KEY,
        settings.TWITTER_REQUEST_TOKEN_URL,
    )

    user_info = client.get_user_info()

    if request.user.is_authenticated():
        # Handling already logged in users connecting their accounts
        try:
            profile = TwitterProfile.objects.get(twitter_id=user_info['id'])
        except TwitterProfile.DoesNotExist: # There can only be one profile!
            profile = TwitterProfile.objects.create(user=request.user,
                                                    twitter_id=user_info['id'], 
                                                    screen_name=user_info['screen_name'])

        return HttpResponseRedirect(_get_next(request))

    user = authenticate(twitter_id=user_info['id'])

    if user is None:
        user = create_user([user_info['screen_name'],]) 
        profile = TwitterProfile.objects.get_or_create(user=user, 
                                                       twitter_id=user_info['id'],
                                                       screen_name=user_info['screen_name'])[0]
        user = profile.authenticate()
        _login(request, user, profile, client)

        return HttpResponseRedirect(user.profile.get_absolute_url())

    _login(request, user, TwitterProfile.objects.get(user = user), client)

    return HttpResponseRedirect(user.profile.get_absolute_url())

def oauth_redirect(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, parameters=None, client_class = None):
    """
    View to handle the OAuth based authentication redirect to the service provider
    """
    request.session['next'] = _get_next(request)
    client = client_class(request, consumer_key, secret_key,
        request_token_url, access_token_url, authorization_url, callback_url, parameters)
    return client.get_redirect()

def oauth_callback(request, consumer_key=None, secret_key=None,
    request_token_url=None, access_token_url=None, authorization_url=None,
    callback_url=None, template='socialregistration/oauthcallback.html',
    extra_context=dict(), parameters=None, client_class = None):
    """
    View to handle final steps of OAuth based authentication where the user
    gets redirected back to from the service provider
    """
    client = client_class(request, consumer_key, secret_key, request_token_url,
        access_token_url, authorization_url, callback_url, parameters)

    extra_context.update(dict(oauth_client=client))
    if not client.is_valid():
        return render_to_response(
            template, extra_context, context_instance=RequestContext(request)
        )

    # We're redirecting to the setup view for this oauth service
    return HttpResponseRedirect(reverse(client.callback_url))

