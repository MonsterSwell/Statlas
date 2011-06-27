from django import template
register = template.Library()

@register.filter('classname')
def classname(ob):
    return ob.__class__.__name__
