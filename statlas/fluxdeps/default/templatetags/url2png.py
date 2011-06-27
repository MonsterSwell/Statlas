"""
A tag that creates an url2png link from a url
"""

from django import template
from django.template import defaultfilters
import hashlib
from settings import URL2PNG_APIKEY, URL2PNG_BOUNDS, URL2PNG_SECRET

register = template.Library()

@register.filter
def url2png(slug):
  url = 'statlas.nl/embed/' + slug + '/'
  api_key = URL2PNG_APIKEY
  secret = URL2PNG_SECRET
  bounds = URL2PNG_BOUNDS
  token = hashlib.md5( "%s+%s" % (secret, url) ).hexdigest()
  return "http://api.url2png.com/v3/%s/%s/%s/%s" % (api_key, token, bounds, url)

