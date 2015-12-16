#https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
#copied code for celery test
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app