"""
Celery tasks for long running searches
http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
"""
from __future__ import absolute_import
from requests.packages.urllib3.exceptions import ReadTimeoutError
import tweepy
from celery import shared_task
from twitter.tweepy import TwitterTweepy
from twitter.tweepy import TweetsStreamListener
from twitter.util import get_twitter_keys_with_user_id, zip_directory
from threading import Timer
from datetime import datetime, timedelta
import time
import os
import csv
from django.db import connection
import logging
from django.core.mail import send_mail
from twitter.models import SearchTask


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
    Tweets of the user timeline will be collected (up to 3200)
    :param names_list:
    """
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    # the following commented out search only searched for tweets seven days in the past
    # my_tweepy.get_tweets_names_searchapi(query_params=names_list, task_id=task_id)
    # new search uses timeline to do the search
    my_tweepy.get_tweets_timeline(names=names_list, task_id=task_id)
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
    # the stream should continue on TypeError
    continue_streaming = True
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
    while continue_streaming:
        try:
            my_stream.filter(follow=user_ids)
            # stop stream on disconnect
            logger.debug("Stop the name stream on disconnect")
            continue_streaming = False
        except (TypeError, ReadTimeoutError, AttributeError):
            # continue the streaming on typeError
            logger.debug("Type error in tweets by name streaming, continue")
            pass


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
    # the stream should continue on TypeError
    continue_streaming = True
    task_id = self.request.id
    keys = get_twitter_keys_with_user_id(user_id)
    # use user-level authentication for streaming (otherwise 401 error)
    my_tweepy = TwitterTweepy(keys=keys, authentication='user_level')
    my_listener = TweetsStreamListener(my_tweepy.api, task_id=task_id)
    my_stream = tweepy.Stream(auth=my_tweepy.api.auth, listener=my_listener)
    # start the scheduling of the stop event
    t = Timer(1.0, schedule_stop_stream, kwargs={'stream': my_stream, 'nr_of_days': nr_of_days, 'task_id': task_id,
                                                 'email': email})
    t.start()
    logger.debug("start streaming search")
    while continue_streaming:
        try:
            my_stream.filter(track=searchterms)
            # stop stream on disconnect
            logger.debug("Seachterm stream disconnect")
            continue_streaming = False
        except (TypeError, ReadTimeoutError, AttributeError):
            # continue the streamin on typeError
            logger.debug("Type error in searchterm streaming")
            pass
    logger.debug("end of streaming")


@shared_task(bind=True)
def collect_random_tweets(self, user_id, email):
    """
    Collect random tweets from the search api
    :param email: the email address of the user
    """
    logger = logging.getLogger('twitter')
    logger.debug("Task: collect random tweets")
    task_id = self.request.id
    logger.debug("task id: {0}".format(task_id))
    keys = get_twitter_keys_with_user_id(user_id)
    my_tweepy = TwitterTweepy(keys)
    my_tweepy.collect_random_tweets(task_id=task_id)
    store_data(search_name="tweets", task_id=task_id, email=email)


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
    logger = logging.getLogger('twitter')
    if search_name == "profile information":
        all_users_from_query(task_id)
        all_relations_from_query(task_id)
        all_list_memberships_from_query(task_id)
        all_list_subscriptions_from_query(task_id)
        # compress the directory for later sending
        zip_and_save_directory(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except:
                logger.debug("Mail could not be sent")
    elif search_name == "tweets":
        all_tweets_from_query(task_id)
        # compress the directory for later sending
        zip_and_save_directory(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except:
                logger.debug("Mail could not be sent")


def zip_and_save_directory(task_id):
    logger = logging.getLogger('twitter')
    try:
        search_task = SearchTask.objects.get(task=task_id)
        path = search_task.csv_path
        zip_path = zip_directory(path=path, task_id=task_id)
        search_task.csv_path = zip_path
        search_task.save()
    except SearchTask.DoesNotExist:
        logger.debug("zip and save directory: task does not exist")


def create_csv_file(name, task_id):
    """
    create a csv file with a certain name and a timestamp with milliseconds
    :param name:
    :return:
    """
    logger = logging.getLogger('twitter')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_dir = os.path.join(base_dir, 'csv_data')
    # make a directory to store the data
    # the directory will be compressed and sent to the user
    data_dir = os.path.join(csv_dir, task_id)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    csv_file_name = name + "_" + date.replace(" ", "_").replace(":", "_").replace("-", "_") + ".csv"
    csv_path = os.path.join(data_dir, csv_file_name)
    csv_file = open(csv_path, 'w+', encoding='utf_8_sig')
    # save the path of the directory to the db for later sending through nginx
    try:
        search_task = SearchTask.objects.get(task=task_id)
        search_task.csv_path = data_dir
        search_task.save()
    except SearchTask.DoesNotExist:
        logger.debug("Problem with saving path of csv file")
    return csv_file


def all_users_from_query(task_id):
    csv_file = create_csv_file("users", task_id=task_id)
    query = "SELECT u.user_id, u.name, u.screen_name, u.friends_count, u.followers_count, u.is_protected, " \
            "u.max_followers_exceeded, u.date_created, u.default_profile_image, u.language, u.location, " \
            "u.profile_image_url, u.user_description, u.verified, u.url FROM twitter_twitteruser u " \
            "WHERE u.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_relations_from_query(task_id):
    csv_file = create_csv_file("relations_query", task_id=task_id)
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
    csv_file = create_csv_file("list_membership", task_id=task_id)
    query = "SELECT user.user_id, user.screen_name, list.list_id, list.list_name, list.list_full_name FROM twitter_twitterlist list " \
            "INNER JOIN twitter_twitterlist_user_membership mem ON mem.twitterlist_id = list.list_id " \
            "INNER JOIN twitter_twitteruser user ON mem.twitteruser_id = user.user_id " \
            "WHERE list.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_list_subscriptions_from_query(task_id):
    csv_file = create_csv_file("list_subscriptions", task_id=task_id)
    query = "SELECT user.user_id, user.screen_name, list.list_id, list.list_name, list.list_full_name FROM twitter_twitterlist list " \
            "INNER JOIN twitter_twitterlist_user_subscription sub ON sub.twitterlist_id = list.list_id " \
            "INNER JOIN twitter_twitteruser user ON sub.twitteruser_id = user.user_id " \
            "WHERE list.task_id LIKE '{}'".format(task_id)
    write_cursor_to_csv(query, csv_file)


def all_tweets_from_query(task_id):
    csv_file = create_csv_file("tweets_search_api", task_id=task_id)
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
    csv_writer = csv.writer(csv_file, dialect="excel")
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)
    csv_file.close()
    del csv_writer
