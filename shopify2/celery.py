from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify2.settings')

app = Celery('shopify2')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
