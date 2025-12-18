import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Agent_Powered_Resume_Analyzer.settings')

# Create the Celery app
app = Celery('AI_Agent_Powered_Resume_Analyzer')

# Load config from Django settings.
# namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()