from django.db import models
from django.db.models import Q


class RegionSetManager(models.Manager):
    pass

class VisibleRegionSetManager(RegionSetManager):
    """
        Returns objects with `visible=True` only
    """
    def get_query_set(self):
        return super(VisibleRegionSetManager, self)\
                .get_query_set()\
                .filter(visible=True)        

class DataSetManager(models.Manager):
    pass

class DataValueManager(models.Manager):
    use_for_related_fields = True
    
    def by_region(self, region_set):
        """
            Throws RegionSet.DoesNotExist
        """
        from models import RegionSet, DataSet, DataValue
        if not hasattr(self, 'core_filters'):
            raise TypeError("The by_region method is only available to the ReleatedManager")
        
        if not isinstance(region_set, RegionSet):
            region_set = RegionSet.objects.get(slug=region_set)
        
        data_set_id = self.core_filters['dataset__id']
        
        if data_set_id: # Allow empty data_set__id (means DataSet == empty)
            data_set = DataSet.objects.get(regionset=region_set, id=data_set_id)            
        else:
            data_set = DataSet(regionset=region_set)

        data    = data_set.data_values.all().select_related('region')

    
        data_values = {}
        for r in region_set.regions.all(): # O(N)
            data_values[r.slug] = DataValue(region=r, dataset=data_set)
    
        for d in data: # O(N)
            data_values[d.region.slug] = d       
        
        return data_values


class PublicDataSetManager(DataSetManager):
    """
        Returns objects with `public=True` only
    """
    def get_query_set(self):
        return super(PublicDataSetManager, self)\
                .get_query_set()\
                .filter(public=True)

