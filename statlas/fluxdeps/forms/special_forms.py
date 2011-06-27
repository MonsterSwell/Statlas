from django import forms
from django.db.models import Q
import operator

class FilterForm(forms.Form):
    """
      BaseForm to create a filterable form. Specify the following:
      
        class Meta:
          model   = Modelname
          fields  = Fields to display
          search_fields = Fields to search using freesearch
          
          (queryset)
    """
    free_search = forms.CharField(required=False)

        
    def __init__(self, queryset=None, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.queryset = queryset if queryset!=None else self.Meta.model.objects
        
    def _apply_free_search(self, qs):
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        terms = self.cleaned_data['free_search'].split(' ')
        if self.Meta.search_fields:
            for term in terms:
                or_queries = [Q(**{construct_search(str(field_name)): term}) for field_name in self.Meta.search_fields]
                qs = qs.filter(reduce(operator.or_, or_queries))
            for field_name in self.Meta.search_fields:
                if '__' in field_name:
                    qs = qs.distinct()
                    break  
                
        return qs
     
    def is_active(self):
        if self.is_valid():
            return len(self.cleaned_data)>0
        
        return False
        
    def custom_filters(self, queryset):
        return queryset
        
    def filtered_results(self, queryset=None):
        qs = queryset if queryset!=None else self.queryset

        if self.is_valid():
            qs = self._apply_free_search(qs)
            qs = self.custom_filters(qs)
            
        return qs.all()