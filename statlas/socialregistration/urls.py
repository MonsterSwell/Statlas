"""

Updated on 19.12.2009

@author: alen, pinda
"""
from django.conf import settings
from django.conf.urls.defaults import *

from socialregistration.utils import OAuthClient, OAuthTwitter


urlpatterns = patterns('',
    url('^logout/$', 'socialregistration.views.logout',
        name='social_logout'),
)

#Setup Twitter URLs if there's an API key specified
if getattr(settings, 'TWITTER_CONSUMER_KEY', None) is not None:
    urlpatterns = urlpatterns + patterns('',
        url('^twitter/redirect/$', 'socialregistration.views.oauth_redirect',
            dict(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                secret_key=settings.TWITTER_CONSUMER_SECRET_KEY,
                request_token_url=settings.TWITTER_REQUEST_TOKEN_URL,
                access_token_url=settings.TWITTER_ACCESS_TOKEN_URL,
                authorization_url=settings.TWITTER_AUTHORIZATION_URL,
                callback_url='twitter_callback',
                client_class = OAuthClient
            ),
            name='twitter_redirect'),

        url('^twitter/callback/$', 'socialregistration.views.oauth_callback',
            dict(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                secret_key=settings.TWITTER_CONSUMER_SECRET_KEY,
                request_token_url=settings.TWITTER_REQUEST_TOKEN_URL,
                access_token_url=settings.TWITTER_ACCESS_TOKEN_URL,
                authorization_url=settings.TWITTER_AUTHORIZATION_URL,
                callback_url='twitter',
                client_class = OAuthClient
            ),
            name='twitter_callback'
        ),
        url('^twitter/$', 'socialregistration.views.twitter', {'client_class': OAuthTwitter}, name='twitter'),
    )

