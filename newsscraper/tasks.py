import logging
from celery import shared_task
from newsscraper.archive_scraper import standaard_scrape, init_driver_firefox, hln_scrape
from newsscraper.util import store_data

@shared_task(bind=True)
def standaard_archive_scrape(self, search_word, start_date, end_date, email):
    """
    Scrapes the archive of the newspaper The Standaard
    http://www.standaard.be/zoeken?keyword=
    :param search_word: The word to search on
    :param start_date: The startDate of the search
    :param end_date: The end date of the search
    """
    logger = logging.getLogger('newsscraper')
    task_id = self.request.id
    logger.debug("Task id: {0}".format(task_id))
    # initalize driver here to close it on exit
    driver = init_driver_firefox()
    # start scrape
    try:
        standaard_scrape(task_id=task_id, search_word=search_word, driver=driver, start_date=start_date, end_date=end_date)
        # write the data of scrape to a file and store the path
        store_data(news_site='standaard', task_id=task_id, email=email)
        # close driver
        # use quit instead of close
        # http://stackoverflow.com/questions/15067107/difference-between-webdriver-dispose-close-and-quit
        driver.quit()
    except Exception as e:
        logger.debug("Problem in standaard scrape: {0}".format(e))
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.debug("Problem closing driver or display: {0}".format(e))


@shared_task(bind=True)
def hln_archive_scrape(self, search_word, start_date, end_date, email):
    """
    Scrapes the archive of the newspaper Het Laatste Nieuws
    :param search_word:
    :param start_date:
    :param end_date:
    :param email:
    :return:
    """
    logger = logging.getLogger('newsscraper')
    task_id = self.request.id
    logger.debug("Task id: {0}".format(task_id))
    # initalize driver here to close it on exit
    driver = init_driver_firefox()
    # start scrape
    try:
        hln_scrape(task_id=task_id, search_word=search_word, driver=driver, start_date=start_date, end_date=end_date)
        store_data(news_site='hln', task_id=task_id, email=email)
    except Exception as e:
        logger.debug("Problem in hln scrape: {0}".format(e))
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.debug("Problem closing driver or display: {0}".format(e))