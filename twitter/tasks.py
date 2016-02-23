"""
Celery tasks for long running searches
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
"""
from __future__ import absolute_import
import tweepy
from celery import shared_task
from twitter.tweepy import TwitterTweepy
from twitter.tweepy import TweetsStreamListener
from twitter.util import get_twitter_keys_with_user_id
from threading import Timer
from datetime import datetime, timedelta
import time
import os
import csv
from django.db import connection
import logging
from django.core.mail import send_mail


@shared_task(bind=True)
def profile_information_search_task(self, names, user_id, email, **kwargs):
    """
    Start the profile information search in background, based on search params entered in homescreen
    Search started in view profile_information_search
    :param names:
    :param user_id:
    :param email:
    :param friends:
    :param followers:
    :param max_followers:
    :param list_memberships:
    :param list_subscriptions:
    """
    logger = logging.getLogger('twitter')
    task_id = self.request.id
    logger.debug("Task id: {0}".format(task_id))
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.profile_information_search(names=names, task_id=task_id, **kwargs)
    # store profile information to csv file and
    store_data(search_name="profile information", task_id=task_id, email=email)


@shared_task(bind=True)
def start_tweets_names_searchapi(self, names_list, user_id, email):
    """
    Get tweets based on names via Search API
    Tweets of 7 days in the past will be collected
    :param names_list:
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_names_searchapi(query_params=names_list, task_id=task_id)
    store_data(search_name="tweets", task_id=task_id, email=email)


@shared_task(bind=True)
def start_tweets_by_name_streaming(self, user_ids, user_id, nr_of_days, email):
    """
    http://docs.tweepy.org/en/latest/streaming_how_to.html (18-12-2015)
    Get tweets based on the names in the names-list
    Data is stored in the function that stops the stream
    With the streaming api
    :param names: list of userids to follow
    """
    logger = logging.getLogger('twitter')
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api, task_id=task_id)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener, task_id=task_id)
    t = Timer(1.0, schedule_stop_stream, kwargs={'stream': my_stream, 'nr_of_days': nr_of_days, 'task_id': task_id,
                                                 'email': email})
    t.start()
    logger.debug("start streaming search")
    my_stream.filter(follow=user_ids)


@shared_task(bind=True)
def start_tweets_searchterms_searchapi(self, searchterms, user_id, email):
    """
    Get tweets based on search terms via Search API
    Tweets of 7 days in the past will be collected
    :param searchterms: a list of searchterms to track
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.get_tweets_searchterms_searchapi(query_params=searchterms, task_id=task_id)
    store_data(search_name="tweets", task_id=task_id, email=email)


@shared_task(bind=True)
def start_tweets_searchterms_streaming(self, searchterms, user_id, nr_of_days, email):
    """
    Get tweets based on searchterms via Streaming API
    :param searchterms: a list of searchterms to track
    :param user_id: id of user, needed to find keys
    :param nr_of_days: the number of days to run the search
    :param email: email address of the user, to send mail when csv file is ready
    """
    logger = logging.getLogger('twitter')
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api, task_id=task_id)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener)
    # start a thread with a timer to stop the streaming
    # time_to_run = float(60 * 60 * 24 * nr_of_days)
    # time_to_run = float(1 * 1 * 1 * nr_of_days)
    # logger.debug("Streaming for {0} days (= {1} seconds".format(nr_of_days, time_to_run))
    # start the scheduling of the stop event
    t = Timer(1.0, schedule_stop_stream, kwargs={'stream': my_stream, 'nr_of_days': nr_of_days, 'task_id' :task_id,
                                                 'email': email})
    t.start()
    logger.debug("start streaming search")
    my_stream.filter(track=searchterms)
    logger.debug("end of streaming")


def schedule_stop_stream(stream, nr_of_days, task_id, email):
    """
    Stops the stream search after the given number of days
    :param stream:
    :param nr_of_days:
    :param task_id:
    :param email:
    :return:
    """
    # http://code.activestate.com/recipes/577183-wait-to-tomorrow/
    logger = logging.getLogger('twitter')
    current_date = datetime.now()
    date_to_stop = current_date + timedelta(days=int(nr_of_days))
    seconds = (date_to_stop - current_date).total_seconds()
    logger.debug("sleep for {0} seconds".format(str(seconds)))
    time.sleep(seconds)
    logger.debug("disconnecting stream")
    # save the data of the stream
    store_data(search_name="tweets", task_id=task_id, email=email)
    try:
        stream.disconnect()
    except:
        logger.debug("ERROR in stream disconnect")
        pass


def store_data(search_name, task_id, email):
    """
    write the data from a certain search task stored in the database to a csv file
    :param search_name: the name of the search_task (different actions for different search tasks)
    :param task_id: task_id to store the filenames to the database
    """
    if search_name == "profile information":
        all_users_from_query(task_id)
        all_relations_from_query(task_id)
        all_list_memberships_from_query(task_id)
        all_list_subscriptions_from_query(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except:
                pass
    elif search_name == "tweets":
        all_tweets_from_query(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except:
                pass


def create_csv_file(name):
    """
    create a csv file with a certain name and a timestamp with milliseconds
    :param name:
    :return:
    """
    logger = logging.getLogger('twitter')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_dir = os.path.join(base_dir, 'csv_data')
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    csv_file_name = name + "_" + date.replace(" ", "_").replace(":", "_").replace("-", "_") + ".csv"
    csv_path = os.path.join(csv_dir, csv_file_name)
    csv_file = open(csv_path, 'w+', encoding='utf-8')
    return csv_file


def all_users_from_query(task_id):
    csv_file = create_csv_file("users")
    query = "SELECT u.user_id, u.name, u.screen_name, u.friends_count, u.followers_count, u.is_protected, " \
            "u.max_followers_exceeded, u.date_created, u.default_profile_image, u.language, u.location, " \
            "u.profile_image_url, u.user_description, u.verified, u.url FROM twitter_twitteruser u " \
            "WHERE u.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_relations_from_query(task_id):
    csv_file = create_csv_file("relations_query")
    query = "SELECT rel.relation_used AS relation, us.user_id AS from_user_id, us.name AS from_name, " \
            "us.screen_name AS from_screen_name, us.friends_count AS from_friends_count, " \
            "us.followers_count AS from_followers_count, us.is_protected AS from_is_protected, " \
            "us2.name AS to_name, us2.screen_name AS to_screen_name, us2.friends_count AS to_friends_count, " \
            "us2.followers_count AS to_followers_count, us2.is_protected AS to_is_protected " \
            "FROM twitter_twitterrelationship rel JOIN twitter_twitteruser us ON rel.from_user_id = us.user_id " \
            "JOIN twitter_twitteruser us2 ON rel.to_user_id = us2.user_id " \
            "WHERE rel.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_list_memberships_from_query(task_id):
    csv_file = create_csv_file("list_membership")
    query = "SELECT user.user_id, user.screen_name, list.list_id, list.list_name, list.list_full_name FROM twitter_twitterlist list " \
            "INNER JOIN twitter_twitterlist_user_membership mem ON mem.twitterlist_id = list.list_id " \
            "INNER JOIN twitter_twitteruser user ON mem.twitteruser_id = user.user_id " \
            "WHERE list.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_list_subscriptions_from_query(task_id):
    csv_file = create_csv_file("list_subscriptions")
    query = "SELECT user.user_id, user.screen_name, list.list_id, list.list_name, list.list_full_name FROM twitter_twitterlist list " \
            "INNER JOIN twitter_twitterlist_user_subscription sub ON sub.twitterlist_id = list.list_id " \
            "INNER JOIN twitter_twitteruser user ON sub.twitteruser_id = user.user_id " \
            "WHERE list.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_tweets_from_query(task_id):
    csv_file = create_csv_file("tweets_search_api")
    query = "SELECT t.tweet_id, t.tweeter_id, t.tweeter_name, t.tweet_text, t.tweet_date, t.is_retweet, t.mentions, " \
            "t.hashtags, t.hyperlinks, t.coordinates, t.favorite_count, t.id_str, t.in_reply_to_screen_name, " \
            "t.quoted_status_id, t.retweet_count, t.source FROM twitter_tweet t " \
            "WHERE t.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def write_cursor_to_csv(query, csv_file):
    """
    write a raw query to a csv file
    http://stackoverflow.com/questions/6837347/database-to-csv-in-django-using-python
    (04/02/2016)
    :param cursor:
    :param query:
    :param csv_file:
    :return:
    """
    cursor = connection.cursor()
    cursor.execute(query)
    csv_writer = csv.writer(csv_file, delimiter=',')
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)
    csv_file.close()
    del csv_writer
