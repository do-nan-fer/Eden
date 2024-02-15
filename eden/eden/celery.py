# eden/eden/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eden.settings')

app = Celery('eden')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from . import settings  # Ensure settings are imported
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  # Discover tasks in installed apps

# Import your tasks module here to ensure it's loaded
from garden import tasks  
