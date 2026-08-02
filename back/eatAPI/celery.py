from celery import Celery 
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eatAPI.settings')

app = Celery('eatAPI')  

app.config_from_object('django.conf:settings', namespace='CELERY')  

app.autodiscover_tasks()
