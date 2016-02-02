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
from threading import Timer
from datetime import datetime, timedelta
import time
import os
from twitter.models import TwitterUser
import djqscsv


@shared_task(bind=True)
def profile_information_search_task(self, names, user_id, **kwargs):
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
    task_id = self.request.id
    print("Task id: {0}".format(task_id))
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.profile_information_search(names=names, task_id=task_id, **kwargs)
    # store the data of the search
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_dir = os.path.join(base_dir, 'csv_data')
    # store profile information to csv file and
    store_data("profile information", task_id)


@shared_task(bind=True)
def start_tweets_names_searchapi(self, names_list, user_id):
    """
    Get tweets based on names via Search API
    Tweets of 7 days in the past will be collected
    :param names_list:
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_names_searchapi(query_params=names_list, task_id=task_id)


@shared_task(bind=True)
def start_tweets_by_name_streaming(self, user_ids, user_id, nr_of_days):
    """
    http://docs.tweepy.org/en/latest/streaming_how_to.html (18-12-2015)
    Get tweets based on the names in the names-list
    With the streaming api
    :param names: list of userids to follow
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api, task_id=task_id)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener, task_id=task_id)
    t = Timer(1.0, schedule_stop_stream, kwargs={'stream': my_stream, 'nr_of_days': nr_of_days})
    t.start()
    print("start streaming search")
    my_stream.filter(follow=user_ids)


@shared_task(bind=True)
def start_tweets_searchterms_searchapi(self, searchterms, user_id):
    """
    Get tweets based on search terms via Search API
    Tweets of 7 days in the past will be collected
    :param searchterms: a list of searchterms to track
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_searchterms_searchapi(query_params=searchterms, task_id=task_id)


@shared_task(bind=True)
def start_tweets_searchterms_streaming(self, searchterms, user_id, nr_of_days):
    """
    Get tweets based on searchterms via Streaming API
    :param searchterms: a list of searchterms to track
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api, task_id=task_id)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener)
    # start a thread with a timer to stop the streaming
    # time_to_run = float(60 * 60 * 24 * nr_of_days)
    # time_to_run = float(1 * 1 * 1 * nr_of_days)
    # print("Streaming for {0} days (= {1} seconds".format(nr_of_days, time_to_run))
    # start the scheduling of the stop event
    t = Timer(1.0, schedule_stop_stream, kwargs={'stream': my_stream, 'nr_of_days': nr_of_days})
    t.start()
    print("start streaming search")
    my_stream.filter(track=searchterms)
    print("end of streaming")


def schedule_stop_stream(stream, nr_of_days):
    # http://code.activestate.com/recipes/577183-wait-to-tomorrow/
    current_date = datetime.now()
    date_to_stop = current_date + timedelta(days=int(nr_of_days))
    seconds = (date_to_stop - current_date).total_seconds()
    print("sleep for {0} seconds".format(str(seconds)))
    time.sleep(seconds)
    print("disconnecting stream")
    try:
        stream.disconnect()
    except:
        print("ERROR in stream disconnect")
        pass


def store_data(search_name, task_id):
    """
    write the data from a certain search task stored in the database to a csv file
    :param search_name: the name of the search_task (different actions for different search tasks)
    :param task_id: task_id to store the filenames to the database
    """
    if search_name == "profile information":
        qs_twitter_users = TwitterUser.objects.filter(task_id=task_id)
        file_to_write = create_csv_file("friends")
        try:
            djqscsv.write_csv(qs_twitter_users, file_to_write)
        except Exception as e:
            print("Problem with writing csvfile")
        file_to_write.close()


def create_csv_file(name):
    """
    create a csv file with a certain name and a timestamp with milliseconds
    :param name:
    :return:
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_dir = os.path.join(base_dir, 'csv_data')
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    csv_file_name = name + "_" + date.replace(" ", "_").replace(":","_").replace("-","_") + ".csv"
    csv_path = os.path.join(csv_dir, csv_file_name)
    try:
        csv_file = open(csv_path, 'w+', encoding='utf-8')
        return csv_file
    except IOError:
        print("Error writing to csv file")
