"""
WSGI config for miniprogram project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""


import os
import sys  # 4
reload(sys)
sys.setdefaultencoding('utf-8')

from os.path import dirname, abspath
from django.core.wsgi import get_wsgi_application

PROJECT_DIR = dirname(dirname(abspath(__file__)))  # 3

sys.path.insert(0, PROJECT_DIR)  # 5

os.environ["DJANGO_SETTINGS_MODULE"] = "reviewing.settings"  # 7

application = get_wsgi_application()
