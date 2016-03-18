from django.contrib.auth.models import User
from django.db import models


class ScrapeTask(models.Model):
    """
    Represents a scraping task the user has started
    References a task uuid in the djcelery_taskstate table
    """
    user = models.ForeignKey(User, null=True)
    task = models.CharField(max_length=250, null=True)
    data_path = models.CharField(max_length=250, null=True)

