"""
Celery tasks for long running searches
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
"""
from __future__ import absolute_import
import tweepy
from celery import shared_task
from twitter.tweepy import TwitterTweepy
from twitter.tweepy import TweetsStreamListener
from celery.contrib import rdb
from twitter.util import get_twitter_keys_with_user_id


@shared_task
def profile_information_search_task(names, user_id, **kwargs):
    """
    Start the profile information search in background, based on search params entered in homescreen
    Search started in view profile_information_search
    :param names:
    :param friends:
    :param followers:
    :param max_followers:
    :param list_memberships:
    :param list_subscriptions:
    """
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    # rdb.set_trace()
    my_tweepy.profile_information_search(names, **kwargs)


@shared_task
def start_tweets_names_searchapi(names_list, user_id):
    """
    Get tweets based on names via Search API
    Tweets of 7 days in the past will be collected
    :param names_list:
    """
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_names_searchapi(names_list)


@shared_task
def start_tweets_by_name_streaming(user_ids, user_id):
    """
    http://docs.tweepy.org/en/latest/streaming_how_to.html (18-12-2015)
    Get tweets based on the names in the names-list
    With the streaming api
    :param names: list of userids to follow
    """
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener)
    print("start streaming search")
    my_stream.filter(follow=user_ids)


@shared_task
def start_tweets_searchterms_searchapi(searchterms, user_id):
    """
    Get tweets based on search terms via Search API
    Tweets of 7 days in the past will be collected
    :param searchterms: a list of searchterms to track
    """
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_searchterms_searchapi(searchterms)


@shared_task
def start_tweets_searchterms_streaming(searchterms, user_id):
    """
    Get tweets based on searchterms via Streaming API
    :param searchterms: a list of searchterms to track
    """
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener)
    print("start streaming search")
    my_stream.filter(track=searchterms)



