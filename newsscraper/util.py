from datetime import datetime
import logging
import zipfile
import os
from django.core.mail import send_mail
from newsscraper.models import ScrapeTask
from django.db import connection
import csv


def store_data(news_site, task_id, email):
    """
    write the data from a task stored in the database to a csv file
    :param search_name: the name of the search_task (different actions for different search tasks)
    :param task_id: task_id to store the filenames to the database
    """
    logger = logging.getLogger('newsscraper')
    if news_site == "standaard":
        # write the data to a file
        __write_standaard_scrape_data(task_id)
        # compress the directory for later sending
        __zip_and_save_directory(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except:
                logger.debug("Mail could not be sent")
    elif news_site == "hln":
        # write the data to a file
        __write_hln_scrape_data(task_id)
        # compress the directory for later sending
        __zip_and_save_directory(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com', [email],
                          fail_silently=False)
            except Exception as e:
                logger.debug("Mail could not be sent".format(e))
    elif news_site == "morgen":
        # write the data to a file
        __write_morgen_scrape_data(task_id)
        # compress the directory for later sending
        __zip_and_save_directory(task_id)
        # send mail when task is finished if email address is provided
        if email:
            try:
                send_mail('data ready', 'Twitter datacollection search is finished', 'datacoll3ction@gmail.com',
                          [email],
                          fail_silently=False)
            except Exception as e:
                logger.debug("Mail could not be sent: {0}".format(e))


def __write_standaard_scrape_data(task_id):
    csv_file = __create_csv_file("standaard", task_id=task_id)
    query = "SELECT art.id as article_id, art.newspaper as newspaper_name, art.title as article_title, " \
            "art.hyperlink as article_link, art.date as article_date, art.author as article_author, " \
            "art.source as article_source, art.facebook_shares as article_facebook_shares, " \
            "art.free_article as article_free, art.pin_it as article_pin_it, tw.twitter_link as twitter_link, " \
            "tw.author as twitter_author, tw.lang as twitter_language, tw.date as twitter_date, " \
            "tw.links as twitter_links, tw.hashtags as twitter_hashtags, tw.text as tweet_text " \
            "FROM newsscraper_article art LEFT JOIN newsscraper_embeddedtweet tw ON art.id = tw.article_id " \
            "WHERE art.task_id LIKE '{}'".format(task_id)
    __write_cursor_to_csv(query, csv_file)


def __write_hln_scrape_data(task_id):
    csv_file = __create_csv_file("hln", task_id=task_id)
    query = "SELECT art.id as article_id, art.newspaper as newspaper_name, art.title as article_title, " \
            "art.hyperlink as article_link, art.date as article_date, art.author as article_author, " \
            "art.source as article_source, art.facebook_shares as article_facebook_shares, " \
            "art.free_article as article_free, art.pin_it as article_pin_it, tw.twitter_link as twitter_link, " \
            "tw.author as twitter_author, tw.lang as twitter_language, tw.date as twitter_date, " \
            "tw.links as twitter_links, tw.hashtags as twitter_hashtags, tw.text as tweet_text, " \
            "cm.author as comment_author, cm.text as comment_text, cm.date as comment_date " \
            "FROM newsscraper_article art LEFT JOIN newsscraper_embeddedtweet tw ON art.id = tw.article_id " \
            "LEFT JOIN newsscraper_comment cm ON art.id = cm.article_id " \
            "WHERE art.task_id LIKE '{}'".format(task_id)
    __write_cursor_to_csv(query, csv_file)


def __write_morgen_scrape_data(task_id):
    csv_file = __create_csv_file("morgen", task_id=task_id)
    query = "SELECT art.id as article_id, art.newspaper as newspaper_name, art.title as article_title, " \
            "art.hyperlink as article_link, art.date as article_date, art.author as article_author, " \
            "art.source as article_source, art.facebook_shares as article_facebook_shares, " \
            "art.free_article as article_free, art.pin_it as article_pin_it, tw.twitter_link as twitter_link, " \
            "tw.author as twitter_author, tw.lang as twitter_language, tw.date as twitter_date, " \
            "tw.links as twitter_links, tw.hashtags as twitter_hashtags, tw.text as tweet_text " \
            "FROM newsscraper_article art LEFT JOIN newsscraper_embeddedtweet tw ON art.id = tw.article_id " \
            "WHERE art.task_id LIKE '{}'".format(task_id)
    __write_cursor_to_csv(query, csv_file)
    pass


def __write_cursor_to_csv(query, csv_file):
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
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)
    csv_file.close()
    del csv_writer


def __create_csv_file(name, task_id):
    """
    create a csv file with a certain name and a timestamp with milliseconds
    :param name: name of the csv file
    :return: csv file
    """
    logger = logging.getLogger('newsscraper')
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
        search_task = ScrapeTask.objects.get(task__task_id=task_id)
        search_task.data_path = data_dir
        search_task.save()
    except ScrapeTask.DoesNotExist as e:
        logger.debug("Problem with saving path of csv file: {0}".format(e))
    return csv_file


def __zip_and_save_directory(task_id):
    logger = logging.getLogger('newsscraper')
    try:
        search_task = ScrapeTask.objects.get(task__task_id=task_id)
        path = search_task.data_path
        zip_path = __zip_directory(path=path, task_id=task_id)
        search_task.data_path = zip_path
        search_task.save()
    except ScrapeTask.DoesNotExist as e:
        logger.debug("zip and save directory: task does not exist: {0}".format(e))


def __zip_directory(path, task_id):
    """
    Zips the directory in the path
    # http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    (25/02/2016)
    :param path: the path of the directory
    :return: path of the csv file
    """
    logger = logging.getLogger('twitter')
    file_name = '{0}.zip'.format(task_id)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_dir = os.path.join(base_dir, 'csv_data')
    abs_src = os.path.abspath(path)
    if os.path.isdir(path):
        zipf = zipfile.ZipFile(os.path.join(csv_dir, file_name), 'w', zipfile.ZIP_DEFLATED)
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    # http://stackoverflow.com/questions/27991745/python-zip-file-and-avoid-directory-structure
                    # (25/02/2015)
                    absname = os.path.join(root, file)
                    arcname = absname[len(abs_src) + 1:]
                    zipf.write(os.path.join(root, file), arcname)
        except Exception as e:
            logger.debug("Problem zipping file: {0}".format(e))
        finally:
            zipf.close()
        return os.path.join(csv_dir, file_name)

