from django import template
from django.template.defaultfilters import stringfilter
import datetime


register = template.Library()


class LaTeXString(unicode):
  pass

@register.filter(name = 'latex')
@stringfilter
def latex_repr(obj):
    """ 
    A version of the string repr method, that always outputs variables suitable
    for LaTeXString. 
    """
    # If this has already been processed, it's ok
    if isinstance(obj, LaTeXString):
        return obj
    # Translate strings
    if isinstance(obj, basestring):
        value = unicode(obj).translate(CHAR_ESCAPES).strip()
        return LaTeXString('{%s}' % value)
    # Dates
    elif isinstance(obj, datetime.date):
        return LaTeXString('{%02d-%02d-%02d}' % (obj.year, obj.month, obj.day))
    # Integers
    if isinstance(obj, (int, long)):
        return LaTeXString(str(obj))
    else:
        return LaTeXString(repr(obj))


CHAR_ESCAPES = {
  ord(u'$'): u'\\$',
  ord(u'&'): u'\\&',
  ord(u'%'): u'\\%',
  ord(u'#'): u'\\#',
  ord(u'_'): u'\\_',
  ord(u'\\'): u'\\\\',
  ord(u'\u2018'): u'`',
  ord(u'\u2019'): u"'", 
  ord(u'\u201c'): u"``", 
  ord(u'\u201d'): u"''" ,
  ord(u'\u2014'): u'---', 
  ord(u'\u2013'): u'--',
}
