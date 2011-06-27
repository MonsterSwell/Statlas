"""
    Extensions to template filters
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name = 'truncate')
@stringfilter
def truncate(value, arg, autoescape = None):
    """
    Truncates a string after a certain number of chars.

    Argument: Number of chars to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: 
        return value
    
    escape = conditional_escape if autoescape else lambda x: x

    # Do not count spaces
    value = value.strip()
    if len(value) > length:
        value = '%s&hellip;' % escape(value[:length].rstrip())
    else:
        value = escape(value)
    
    return mark_safe(value)
    
truncate.needs_autoescape = True
