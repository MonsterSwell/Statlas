from django import forms
from django.forms.widgets import RadioSelect
from statmap.models import DataSet, RegionSet
from django.forms import ValidationError
from fluxdeps.forms import FilterForm
from django.contrib.contenttypes.models import ContentType
from accounts.models import LogEntry, ADDITION, CHANGE
from django.utils.encoding import force_unicode

import base64

class FilterMapsForm(FilterForm):
    regionset = forms.ModelChoiceField(queryset=RegionSet.visible_objects.all(), 
                                       widget=RadioSelect,
                                       empty_label='All maps',
                                       required=False)

    def custom_filters(self, queryset):
        cd = self.cleaned_data
        if cd['regionset']:
            queryset = queryset.filter(regionset=cd['regionset'])
     
        return queryset

    class Meta:
        model   = DataSet
        fields  = ('free_search', 'region')
        search_fields = ('title', 'author__username', 'regionset__title', 'description')
    

class MappingForm(forms.ModelForm):
    regionset = forms.ModelChoiceField(queryset=RegionSet.visible_objects.all(), to_field_name='slug')
    
    dataupload = forms.CharField(required=False)
    
    
    def __init__(self, data, user=None, *args, **kwargs):
        self.author = user
        if self.author:
            data = self.parse_post(data)
            instance, self.created = self.fetch_instance(data)
        else:
            instance = None
            self.created = False
            
        super(MappingForm, self).__init__(data, instance=instance, *args, **kwargs)
    
    def parse_post(self, data):
        """
            Parses the form-data. All datasets are provided in the
            format `values[REGION_SLUG] = value`.
        """
        if data:
            parsed_data = { 'values': {}}
            for k in data:
                if k.startswith('values['):
                    parsed_data['values'][k[7:-1]] = data[k]
                elif k.startswith('meta['):
                    parsed_data[k[5:-1]] = data[k]
                else:
                    parsed_data[k] = data[k]
        else:
            parsed_data = []

        return parsed_data

    def fetch_instance(self, data):
        """
            Returns the DataSet saved to our database if available.
            If not available it will return a new DataSet with 
            the author bound to it.
            
            Keep in mind that it is possible that the `User` submits
            a dataset(slug) from a DataSet that is owned by some
            other user. In this case we consider the submission as
            a new DataSet.
        """
        try:
            slug = data['dataset']
            if slug!='empty': # New data set
                instance = DataSet.objects.get(slug=slug, author=self.author)
                created = False
            else:
                raise DataSet.DoesNotExist
        except KeyError: # Slug is not part of the data
            instance = DataSet(author=self.author)
            created = True
        except DataSet.DoesNotExist: # Slug does not exist (for this user) yet
            instance = DataSet(author=self.author)
            created = True
        
            
        return instance, created

    def get_data_from_excel(self, file_contents):
        """
            Read data from CSV file. The format should be:
            
            ------  -----
            Region  Value
            ------  -----
            slug    value
            ------  -----
        """
        from xlrd import open_workbook
        wb = open_workbook(file_contents=file_contents,)
        sh = wb.sheet_by_index(0)
        
        if not sh.cell(0,0)=='Region' and sh.cell(0,1)=='Value':
            raise ValidationError("Did not recognize Excel contents")
        
        data = {}
        for i in range(1, sh.nrows):
            data.update({ sh.cell(i, 0).value: sh.cell(i,1).value })
       
        return data
      
    def get_data_from_csv(self, file_contents):
        """
            Read data from CSV file. The format should be:
            
            ------  -----
            Region  Value
            ------  -----
            slug    value
            ------  -----
        """
        import csv
        
        dialect = csv.Sniffer().sniff(file_contents[:1024])
        csv_file = csv.reader(file_contents.splitlines(), dialect)
        
        table_head = csv_file.next()
        try:
            if not table_head[0]=='Region' and table_head[1]=='Value':
                raise Exception
        except:
            ValidationError("Did not recognize CSV contents")

        data = {}
        while True:
            try:
                row=csv_file.next()
                data.update({ row[0]: row[1] })
            except StopIteration:
                break

        return data
        
    def clean(self, *args, **kwargs):
        cd = self.cleaned_data
        
        if not cd['dataupload']=='':
            try:
                file_type, file_string = cd['dataupload'].split(',')
                file_contents = file_string.decode('base64')
                
                mime_type = file_type[5:].split(';')[0]
                if 'excel' in mime_type:            
                    cd['values'] = self.get_data_from_excel(file_contents)
                elif mime_type == 'text/csv':
                    cd['values'] = self.get_data_from_csv(file_contents)
                else:
                    raise ValueError
            except ValueError:  # Unsupported format
                raise ValidationError("Unsupported received file format %s" % mime_type)    

        else:
            cd['values'] = self.data['values']
        
        return cd
    
    def save(self, *args, **kwargs):
        """
            Saves the DataSet to the server. If the DataSet
            is not new (eg. there are some data_values saved
            already), all old data_values will be removed.
            
            .. NOTE ::
                The save method can only be issued if the
                `User` (author) is provided to the form
                during initialization.
        """
        
        if not self.author:
            raise Exception("Save is only available if a user is passed during initialisation!")
        
        data_set = super(MappingForm, self).save(*args, **kwargs)
        
        data_set.data_values.all().delete()
        
        # Build a regions map for matching datavalues
        regions = data_set.regionset.regions.all()
        regions_map = {}
        for region in regions:
            regions_map[region.slug] = region
        
        values = self.cleaned_data['values']
        for key in values.keys():
            try:
                region = regions_map[key]
                v = data_set.data_values.create(
                    region = region,
                    value  = values[key],
                    dataset = data_set                
                )
                v.save()
            
                del regions_map[key]  # Distinct region
            except KeyError:
                print "Unknown datapoint %s" % key
                pass
            
        LogEntry.objects.log_action(
            user_id         = data_set.author.pk,
            content_type_id = ContentType.objects.get_for_model(data_set).pk,
            object_id       = data_set.pk,
            object_repr     = force_unicode(data_set),
            action_flag     = ADDITION if self.created else CHANGE
        )            
            
            
        return data_set
    
    class Meta:
        model   = DataSet
        exclude = ('author', )
    
