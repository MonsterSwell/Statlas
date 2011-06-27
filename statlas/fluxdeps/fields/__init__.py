"""
    Extensions to default Django fields, used in database models. 

    .. warning:: These can not be used for forms. Place form-fields in
                :mod:`fluxbase`.`forms`.`fields`
"""
from slugfield import SlugField
from markupfield import MarkupField
from markdownfield import MarkdownField
from postalcodefield import PostalcodeField
from autoonetoonefield import AutoOneToOneField
from jsonfield import JSONField

__all__ = ['SlugField', 'MarkupField', 'MarkdownField', 'PostalcodeField'
           ,'AutoOneToOneField', 'JSONField']
