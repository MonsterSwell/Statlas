#!/opt/python2.6/bin/python
import os, sys
sys.path.insert(0,'/home/voorlich/django/')
sys.path.insert(0,'/home/voorlich/django/vomarkt/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'vomarkt.settings'
os.environ['PYTHON_EGG_CACHE'] = '/home/voorlich/django/.python-eggs'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

