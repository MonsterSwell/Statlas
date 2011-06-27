from django.db import models
from fluxdeps.fields import SlugField, MarkdownField
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from settings import IN_PRIVATE_DATA_ROOT, PRIVATE_DATA_ROOT
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, post_delete

import managers

class RegionSet(models.Model):
    """
        The regionset describes the labels in the dataset:
            * Provincie (Zuid-Holland, Noord-Holland, etc.)
            * Municipality (Amsterdam, Rotterdam, etc.)

        Each RegionSet contains a set of labels (regions): :class:`region`.

        .. TODO ::
            Create Storage for geo_json somewhere above media_root
            
            Alper: Would we be storing geo_json both for the regionset as for the regions?
    """
    title       = models.CharField(_('title'), max_length=100)
    slug        = SlugField('title')

    visible     = models.BooleanField(default=True)

    """* MANAGERS *"""
    objects         = managers.RegionSetManager()
    visible_objects = managers.VisibleRegionSetManager()
    
    """* Storage * """
    #storage_location = IN_PRIVATE_DATA_ROOT('regionsets')
    store            = FileSystemStorage(location=PRIVATE_DATA_ROOT)
    _json           = models.FileField(storage=store, upload_to='regionsets', editable=False, blank=True)    
    
    @property
    def json(self):
        import json
        if not self._json:
            features = []
            for region in self.regions.all():
                features += [{
                              'type': 'Feature',
                              'geometry': json.loads(region.geo_json),
                              'properties': {
                                  'citySlug': region.slug,
                                  'cityName': region.title
                              }
                            ,}]
        
            geo_json_return = {
                "type": "FeatureCollection",
                "features": features
            }
        
            content = ContentFile(json.dumps(geo_json_return))
            self._json.save('%s.json' % self.slug, content, True)
        
        return self._json
        
    def get_json_url(self):
        return reverse('statmap:jsdata:region_set_geo', args=[self.slug,])

    class Meta:
        verbose_name        = _('region set')
        verbose_name_plural = _('region sets')

        ordering            = ('title',)

    def __unicode__(self):
        return self.title


class Region(models.Model):
    """
        A region, part of the :class:`RegionSet`. Describes an area on the
        map, for instance 'Zuid-Holland'.

        See also :ref:`RegionSet`
        
        .. TODO ::
            Upload to ../data using filesystemstorage
            
        .. TODO ::
            Hmmm.. I (wouter) don't like to put raw json into the database..
            this could be converted to binary format if we start using GeoDjango.
            But for now we keep it this way
            
            Alper: Do we store GeoJSON in the database? Didn't we agree to 
            store it on the filesystem?
            
            Wout: Not sure if we have discussed that, but I have no problems
            with storing the GeoJSON on the server. I will migrate it
            asap.
 
    """
    regionset   = models.ForeignKey(RegionSet, related_name='regions', verbose_name=_('region set'))
    title       = models.CharField(_('title'), max_length=100)
    slug        = SlugField('title')
    
    geo_json    = models.TextField()
    #geo_json_file = models.FileField(upload_to=IN_SITE_ROOT('data/geojson'))

    class Meta:
        verbose_name        = _('region')
        verbose_name_plural = _('regions')

        ordering            = ('title',)
    
    def __unicode__(self):
        return self.title

class DataSet(models.Model):
    """
        The :class:`mapping`-class maps a dataset to some map.

        .. NOTE ::
            # A mapping (complete or incomplete is on a certain regionset)
            Wout > Alper: what do you mean by this?
            
            Alper: This is the mapping. It is bound by 1 RegionSet that it is pertinent to.
            It can contain 0 or more values for Regions in that Regionset (if it contains 0
            it is an empty mapping due to be filled in at a later point.)
            

    """
    title        = models.CharField(_('title'), max_length=100)
    slug         = SlugField('title', reserved_words=['empty','datasets'])
    description  = MarkdownField(_('description'), blank=True)
    regionset    = models.ForeignKey(RegionSet, related_name='data_sets')
    
    author       = models.ForeignKey(User, related_name="data_sets")

    zoom         = models.CharField(max_length=20)
    latitude     = models.CharField(max_length=20)
    longitude    = models.CharField(max_length=20)       # DecimalField is not serializable by JSON lib
    
    public       = models.BooleanField(_('public'), default=True)
    date_created = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_changed = models.DateTimeField(_('change date'), auto_now=True)
    
    recently_viewed_by  = models.ManyToManyField(User, related_name='recently_viewed_datasets', through='RecentlyViewedDataSet', blank=True, null=True, editable=False)
    favorite_by         = models.ManyToManyField(User, related_name='favorite_datasets', through='FavoriteDataSet', blank=True, null=True, editable=False)    
    
    
    """* Managers *"""
    objects         = managers.DataSetManager()
    public_objects  = managers.PublicDataSetManager()   

    def get_json_url(self):
        return reverse('statmap:jsdata:data_set', args=[self.regionset.slug, self.slug,])

    def get_absolute_url(self):
        return reverse('statmap:mapdetail', args=[self.slug])

    def update_recently_viewed_by(self, user):
        if user.is_authenticated():
            rv, c = RecentlyViewedDataSet.objects.get_or_create(user=user, dataset=self)
            if not c:
                rv.save()

    def is_favorited_by(self, user):
        if not user.is_authenticated():
            return False
          
        return FavoriteDataSet.objects.filter(user=user,
                                              dataset=self) \
                                      .count() > 0

    class Meta:
        verbose_name        = _('data set')
        verbose_name_plural = _('data sets')

        ordering            = ('title','date_changed')

    def __unicode__(self):
        return self.title

class DataValue(models.Model):
    """
        One data-value in the :class:`mapping`.
    """
    dataset     = models.ForeignKey(DataSet, related_name='data_values', verbose_name=_('dataset'))
    region      = models.ForeignKey(Region, related_name='data_values', verbose_name=_('region'))
    value       = models.CharField(max_length=100)

    date_created = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_changed = models.DateTimeField(_('change date'), auto_now=True)

    objects     = managers.DataValueManager() 

    class Meta:
        verbose_name        = _('value')
        verbose_name_plural = _('values')

        ordering            = ('region', 'value')
        
    def __unicode__(self):
        return "%s: %s" % (self.region.title, self.value)

class FavoriteDataSet(models.Model):
    dataset     = models.ForeignKey(DataSet, related_name='favorite_data_set')
    user        = models.ForeignKey(User, related_name='favorite_data_set')
    
    date_created = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_changed = models.DateTimeField(_('change date'), auto_now=True)

class RecentlyViewedDataSet(models.Model):
    dataset     = models.ForeignKey(DataSet, related_name='recently_viewed_data_set')
    user        = models.ForeignKey(User, related_name='recenty_viewed_data_set')
    view_count  = models.PositiveIntegerField(default=0)  
    
    date_created = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_changed = models.DateTimeField(_('change date'), auto_now=True)

    def save(self, *args, **kwargs):
        self.view_count = self.view_count + 1
        super(RecentlyViewedDataSet, self).save(*args, **kwargs)
"""
    Future talk

class MapList(models.Model):
    datecreated = models.DateTimeField()
    datechanged = models.DateTimeField()
    
    mappings = models.ManyToManyField(Mapping)
  
"""    

def flush_cache_region_set(sender, instance, *args, **kwargs):
    try:
        if instance.regionset._json:
            instance.regionset._json.delete()
    except RegionSet.DoesNotExist:
        pass
      
    

post_save.connect(
        flush_cache_region_set
    ,   sender       = Region
    ,   dispatch_uid = "regionset_updated"
)

post_delete.connect(
        flush_cache_region_set
    ,   sender       = Region
    ,   dispatch_uid = "regionset_deleted"
)
