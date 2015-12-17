"""
Celery tasks for long running searches
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
"""

from __future__ import absolute_import
from celery import shared_task
from twitter.tweepy import TwitterTweepy
from celery.contrib import rdb


@shared_task
def profile_information_search_task(names, **kwargs):
    '''
    Start the profile information search in background, based on search params entered in homescreen
    Search started in view profile_information_search
    :param names:
    :param friends:
    :param followers:
    :param max_followers:
    :param list_memberships:
    :param list_subscriptions:
    :return:
    '''

    tweepy = TwitterTweepy()
    #rdb.set_trace()
    tweepy.profile_information_search(names, **kwargs)


