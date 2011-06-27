from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('statmap.views',
    (r'^$', 'explore', (), 'explore'),
    (r'^page-(?P<page>[0-9]+)/$', 'explore', (), 'explore'),

    (r'^create/$', 'create', (), 'create'),
    (r'^create/save/$', 'save', (), 'save'),

    (r'^map/(?P<slug>\w+(-\w+)*)/$', 'mapdetail', (), 'mapdetail'),
    (r'^embed/(?P<slug>\w+(-\w+)*)/$', 'embed', (), 'embed'),

    (r'^map/(?P<slug>\w+(-\w+)*)/favorite/$', 'favorite', (), 'favorite'),
    (r'^map/(?P<slug>\w+(-\w+)*)/unfavorite/$', 'unfavorite', (), 'unfavorite'),


    (r'^jsdata/', include('statmap.urls.json', namespace='jsdata')),

    (r'^download/(?P<region_set_slug>\w+(-\w+)*)_(?P<data_set_slug>\w+(-\w+)*)\.(?P<file_type>(csv|xls))$', 'file_processing.download', (), 'download'),
    (r'^upload/$', 'file_processing.download', (), 'upload'),

    (r'^about/$', 'about'),
)

