from django.contrib.auth.models import User
from django.db import models
from djcelery.models import TaskState


class ScrapeTask(models.Model):
    """
    Represents a scraping task the user has started
    References a task uuid in the djcelery_taskstate table
    """
    user = models.ForeignKey(User, null=True, related_name='user')
    task = models.ForeignKey(TaskState, null=True, related_name='task')
    data_path = models.CharField(max_length=250, null=True)

