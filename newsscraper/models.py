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


class Article(models.Model):
    """
    Represents an article of a newspaper
    """
    newspaper = models.CharField(max_length=250, null=True)
    title = models.CharField(max_length=250, null=True)
    hyperlink = models.CharField(max_length=250, null=True)
    date = models.CharField(max_length=250, null=True)
    author = models.CharField(max_length=250, null=True)
    source = models.CharField(max_length=250, null=True)
    googleplus_shares = models.CharField(max_length=100, null=True)
    twitter_shares = models.CharField(max_length=100, null=True)
    facebook_shares = models.CharField(max_length=100, null=True)
    free_article = models.NullBooleanField(null=True)
    pin_it = models.CharField(max_length=250, null=True)
    video = models.CharField(max_length=250, null=True)
    task_id = models.CharField(max_length=250, null=True)


class EmbeddedTweet(models.Model):
    """
    Represents a tweet inside an article
    """
    article = models.ForeignKey(Article, null=True, related_name='tweet_article')
    twitter_link = models.CharField(max_length=250, null=True)
    author = models.CharField(max_length=250, null=True)
    lang = models.CharField(max_length=100, null=True)
    date = models.CharField(max_length=100, null=True)
    links = models.CharField(max_length=500, null=True)
    hashtags = models.CharField(max_length=250, null=True)
    text = models.CharField(max_length=250, null=True)

class Comment(models.Model):
    """
    Represents a comment inside an HLN article
    """
    article = models.ForeignKey(Article, null=True, related_name='comment_article')
    author = models.CharField(max_length=250, null=True)
    text = models.CharField(max_length=1000, null=True)
    date = models.CharField(max_length=250, null=True)