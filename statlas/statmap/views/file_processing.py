from django.http import HttpResponse
from django.db.models import Q
from django.http import Http404
from datetime import datetime


from statmap.models import DataSet, RegionSet, DataValue
from helper import get_data_set


def download(request, region_set_slug, data_set_slug, file_type):
    """
        Returns the data_values of a `DataSet` in the give format.
        
        Currently we provide the following formats:
        
        * xls
        * csv
    """
    data_set = get_data_set(request.user, data_set_slug, region_set_slug)
    
    if file_type=='xls':
        return download_xls(data_set)
    elif file_type=='csv':
        return download_csv(data_set)
    else: # Unknown filetype
        raise Http404

def download_xls(data_set):
    from xlutils.copy import copy
    from xlrd import open_workbook
    from settings import IN_SITE_ROOT

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s_%s-%s.xls' % (data_set.regionset.slug, data_set.slug, datetime.now().strftime('%Y%m%d-%H%M'))

    base = open_workbook(IN_SITE_ROOT('templates/statmap/base_dataset.xls'), formatting_info=True)
    wb = copy(base)
    ws = wb.get_sheet(0)

    values = data_set.data_values.by_region(data_set.regionset).values()
    
    values.sort(key=lambda dv: dv.region.title)
    
    for i, value in enumerate(values, 1):
        ws.write(i, 0, value.region.slug)
        ws.write(i, 1, value.value)

    wb.save(response)

    return response

def download_csv(data_set):
    import csv
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_%s-%s.csv' % (data_set.regionset.slug, data_set.slug, datetime.now().strftime('%Y%m%d-%H%M'))

    ws = csv.writer(response)

    values = data_set.data_values.by_region(data_set.regionset)

    ws.writerow(['Region', 'Value'])
    for v in values.itervalues():
        ws.writerow([v.region.slug, v.value])

    return response    
    
def upload(request, file_type):
    pass