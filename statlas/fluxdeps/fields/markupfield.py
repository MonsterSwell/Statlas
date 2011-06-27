from django.utils.safestring import mark_safe
from django.db import models
from django import forms
from django.forms import widgets

class MarkupInput(forms.Field):
    def __init__(self, *args, **kwargs):
        """Input for markup content.

        :param widget: unless specified otherwise, this defaults to a textarea.
        """

        if not 'widget' in kwargs:
            kwargs['widget'] = widgets.Textarea()
            
        super(MarkupInput, self).__init__(*args, **kwargs)
            
class MarkupField(models.TextField):
    """Model field that contains markup content and automatically cached it in
    an associated field"""
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        # For Django-South compatibility
        self.addRenderedField = not kwargs.pop('no_rendered_field', False)
                        
        # Initialize as if this simply was a TextField.
        super(MarkupField, self).__init__(*args, **kwargs)
    
    def process_markup(self, content):
        """Subclasses should override this method.

        This method provides the means to actually render the content. It should
        yield a unicode result, of rendered markup as provided by content.

        :param content: raw markup
        """
        return content
            
    def contribute_to_class(self, cls, name):
        # Prepare field-names
        self.renderedName = '%s_rendered' % name
        
        # Add field for rendered content, whenever necessary
        if self.addRenderedField:
            renderedField = models.TextField(editable = False)
            renderedField.creation_counter = self.creation_counter + 1
            
            cls.add_to_class(self.renderedName, renderedField)
        
        # Add this field, wrapped to allow easy access
        super(MarkupField, self).contribute_to_class(cls, name)
        
        setattr(cls, self.name + '_', MarkupContent(self))
    
    def yieldData(self, value):
        if isinstance(value, ContentContainer):
            raw      = value.raw
            rendered = value.rendered
        elif isinstance(value, unicode) or isinstance(value, str):
            raw      = value
            rendered = self.process_markup(raw)
        else:
            raw = rendered = u''
            
        return raw, rendered
    
    def pre_save(self, instance, add):
        value = super(MarkupField, self).pre_save(instance, add)

        raw, rendered = self.yieldData(value)
        
        instance.__dict__[self.name] = raw
        instance.__dict__[self.renderedName] = rendered

        return raw
    
    def formfield(self, **kwargs):  
        inputField = self.markupInputClass
        inputField.process_markup = self.process_markup
        
        defaults = { 'form_class' : inputField}
        defaults.update(kwargs)
        
        return super(MarkupField, self).formfield(**defaults)

    markupInputClass = MarkupInput

class MarkupContent(object):
    """Wrapper around markup content"""
    def __init__(self, field):
        self.field = field
        
    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')
        
        raw_data = instance.__dict__[self.field.name]
        
        if raw_data is None:
            return None
            
        return ContentContainer(
                instance     = instance
            ,   rawName      = self.field.name
            ,   renderedName = self.field.renderedName
        )

    def __set__(self, obj, value):
        raw, rendered = self.field.yieldData(value)
        
        obj.__dict__[self.field.name] = raw
        obj.__dict__[self.field.renderedName] = rendered

class ContentContainer():
    """Wrapper class around a MarkupField.
    This class has attriutes, raw and rendered, which contain the obvious. If you request the unicode-
    content of this class, it yields the rendered text."""
    
    def __init__(self, instance, rawName, renderedName):
        self.instance = instance
        self.rawName = rawName
        self.renderedName = renderedName
    
    raw = property(
            lambda self: self.instance.__dict__[self.rawName]
        ,   lambda self, value: setattr(self.instance, self.rawName, value)    
        ,   doc = "Raw content of this field"
    )
    rendered = property(
            lambda self: self.instance.__dict__[self.renderedName]
        ,   doc = "Rendered version of the raw content of this field"
    )
        
    def __unicode__(self):
        return mark_safe(self.rendered)
    
    def __str__(self):
        return unicode(self).encode('ascii', 'replace')
        
# Ensure that south knows what to do
HAS_SOUTH = True
try:
    from south.modelsinspector import add_introspection_rules
except ImportError as exp:
    HAS_SOUTH = False

if HAS_SOUTH:
    add_introspection_rules(
        rules = [
            (
                    (MarkupField,)
                ,   []
                ,   {
                    'no_rendered_field': 
                        (
                                'addRenderedField'
                            ,   {}
                        )
                    }
            )]
        , patterns = [r'^fluxbase\.fields.\markupfield\.MarkupField$']
    )
