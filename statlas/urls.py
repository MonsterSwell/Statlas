from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout

import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^social/', include('socialregistration.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/', include('accounts.urls', namespace="accounts")),
    
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    url(r'^logout/$', logout, (), name = 'auth_logout'),
        
    (r'^', include('statmap.urls', namespace='statmap')),
)


if settings.DEBUG:
  urlpatterns = patterns('django.views.generic.simple',
    (r'^404/$', 'direct_to_template', {'template': '404.html'}),
    (r'^500/$', 'direct_to_template', {'template': '500.html'}),
  ) + urlpatterns


