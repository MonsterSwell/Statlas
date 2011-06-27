from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import json


from statmap.models import RegionSet, Region, DataSet



class Command(BaseCommand):
    help =  """
                Create a RegionSet and if available also the datasets
                (based on the properties)
                
                dj create_regionset "Nederlandse Gemeenten" data/private/pre_data/wgs84.gem_2008_gn2.geo.json GM_NAAM
                dj create_regionset "Nederlandse buurten" data/private/pre_data/wgs84.brt_2008_gn2.geo.json BU_NAAM
                dj create_regionset "Amsterdamse wijken" data/private/pre_data/wgs84.wijken_amsterdam.json WK_NAAM
                dj create_regionset "Nederlandse wijken" data/private/pre_data/wgs84.wijk_2008_gn2.geo.json WK_NAAM
            """

    args = "<regionset_title path region_title_field [dataset1] [dateset2] etc..>"

    def handle(self, regionset_title, path, region_title_field, *args, **kwargs):
        user = User.objects.get(username="monsterswell")
      
        print "Start importing %s from %s" % (regionset_title, path)
        regionset, c = RegionSet.objects.get_or_create(title=regionset_title)
        
        fp = open(path, 'r')
        data = json.loads(fp.read().encode('utf-8'))
        
        if c:
            print " * Created new regionset for %s" % regionset_title
        else:
            print " * Use existing regionset"

        try:
            testset = data['features'][0]
        except KeyError:
            print "JSON file has no attribute features or contains no features"
        
        print " * Detect datasets to analyse"
        datasets = []
        for d in testset['properties']:
            print "   + Found %s.." % d,
            if region_title_field==d:
                print "SKIP"
                continue
              
            # Remove previous version :-)
            try:
                DataSet.objects.get(regionset=regionset, author=user, title=d).delete()
                print "REMOVE OLD AND", 
            except DataSet.DoesNotExist:
                pass

            print "ADDED NEW"
            datasets += [DataSet.objects.create(regionset=regionset, author=user, title=d),]
        
        del testset

        for r in data['features']:
            print " - Process %s" % r["properties"][region_title_field].encode('utf-8')
            region = self.get_or_create_region(regionset,
                                               r["properties"][region_title_field],
                                               json.dumps(r['geometry']),
                                               c)
            
            for dataset in datasets:
                d = dataset.data_values.create(region=region, value=r["properties"][dataset.title])
                #print "   + Added value %s for dataset %s" % (d.value, dataset.title) 
                
    def get_or_create_region(self, regionset, title, geo_json, create):
        if create:
            print " + Create region %s" % title.encode('utf-8')
            return regionset.regions.create(title=title.encode('utf-8'),
                                         geo_json=geo_json)
        else:
            try:
                r = regionset.regions.get(title=title.encode('utf-8'))
                return r
            except Region.DoesNotExist:
                print " X Region %s does not exist" % title.encode('utf-8')
                return self.get_or_create_region(regionset, title, geo_json, True)
            
