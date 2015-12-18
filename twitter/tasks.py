"""
Celery tasks for long running searches
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
"""
import tweepy
from __future__ import absolute_import
from celery import shared_task
from twitter.tweepy import TwitterTweepy
from twitter.tweepy import TweetsByNameStreamListener
from celery.contrib import rdb


@shared_task
def profile_information_search_task(names, **kwargs):
    """
    Start the profile information search in background, based on search params entered in homescreen
    Search started in view profile_information_search
    :param names:
    :param friends:
    :param followers:
    :param max_followers:
    :param list_memberships:
    :param list_subscriptions:
    :return:
    """
    my_tweepy = TwitterTweepy()
    # rdb.set_trace()
    my_tweepy.profile_information_search(names, **kwargs)


@shared_task
def start_tweets_by_name_streaming(user_ids):
    """
    http://docs.tweepy.org/en/latest/streaming_how_to.html (18-12-2015)
    Get tweets based on the names in the names-list
    With the streaming api
    :param names: list of userids to follow
    """
    my_tweepy = TwitterTweepy()
    my_listener = TweetsByNameStreamListener()
    my_stream = tweepy.Stream(auth=my_tweepy.api, listener=my_listener())
    my_stream.filter(follow=user_ids)






