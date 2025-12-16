"""
ASGI config for AI_Agent_Powered_Resume_Analyzer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Agent_Powered_Resume_Analyzer.settings')

application = get_asgi_application()
