from django.contrib import admin

from models import DataSet, RegionSet, Region, DataValue

admin.site.register(DataSet)
admin.site.register(RegionSet)
admin.site.register(Region)
admin.site.register(DataValue)

