from django.conf.urls.defaults import patterns

urlpatterns = patterns('accounts.views',
    (r'^(?P<username>\w+(-\w+)*)/$', 'profile', (), 'profile'),
    
)
