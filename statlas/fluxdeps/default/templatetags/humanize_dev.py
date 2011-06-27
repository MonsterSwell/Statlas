"""
  A set of tags from the humamnize templatetag only
  available in the Django dev version
"""
from datetime import  timedelta

from django import template
from django.template import defaultfilters
from django.utils.datetime_safe import datetime
from django.utils.translation import pgettext, ungettext, ugettext as _
from django.utils.tzinfo import LocalTimezone


register = template.Library()

@register.filter
def naturaltime(value):
    """
    For date and time values shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.
    """
    try:
        value = datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
    except AttributeError:
        return value
    except ValueError:
        return value

    if getattr(value, 'tzinfo', None):
        now = datetime.now(LocalTimezone(value))
    else:
        now = datetime.now()
    now = now - timedelta(0, 0, now.microsecond)
    if value < now:
        delta = now - value
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timesince(value)}
        elif delta.seconds == 0:
            return _(u'now')
        elif delta.seconds < 60:
            return ungettext(
                u'a second ago', u'%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds / 60 < 60:
            count = delta.seconds / 60
            return ungettext(
                u'a minute ago', u'%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds / 60 / 60
            return ungettext(
                u'an hour ago', u'%(count)s hours ago', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s from now'
            ) % {'delta': defaultfilters.timeuntil(value)}
        elif delta.seconds == 0:
            return _(u'now')
        elif delta.seconds < 60:
            return ungettext(
                u'a second from now', u'%(count)s seconds from now', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds / 60 < 60:
            count = delta.seconds / 60
            return ungettext(
                u'a minute from now', u'%(count)s minutes from now', count
            ) % {'count': count}
        else:
            count = delta.seconds / 60 / 60
            return ungettext(
                u'an hour from now', u'%(count)s hours from now', count
            ) % {'count': count}