from django.conf.urls.defaults import patterns

urlpatterns = patterns('statmap.views.jsondata',
    (r'^regionsets\.json$', 'region_set_list', (), 'region_set_list'),
    (r'^regionsets/(?P<region_set_slug>\w+(-\w+)*)\.json$', 'region_set_geo', (), 'region_set_geo'),
    (r'^regionsets/(?P<region_set_slug>\w+(-\w+)*)/datasets\.json$', 'data_set_list', (), 'data_set_list'),
    (r'^regionsets/(?P<region_set_slug>\w+(-\w+)*)/(?P<data_set_slug>\w+(-\w+)*)\.json$', 'data_set', (), 'data_set'),
)
