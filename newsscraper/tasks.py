import logging
from celery import shared_task
from newsscraper.archive_scraper import standaard_scrape


@shared_task(bind=True)
def standaard_archive_scrape(self, start_date, end_date):
    """
    Scrapes the archive of the newspaper The Standaard
    http://www.standaard.be/zoeken?keyword=
    :param start_date: The startDate of the search
    :param end_date: The end date of the search
    """
    logger = logging.getLogger('newsscraper')
    task_id = self.request.id
    logger.debug("Task id: {0}".format(task_id))
    standaard_scrape(task_id=task_id, start_date=start_date, end_date=end_date)

