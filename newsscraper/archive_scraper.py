import json
import logging
from bs4 import BeautifulSoup
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchFrameException, StaleElementReferenceException, TimeoutException, \
    NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from newsscraper.models import Article, EmbeddedTweet, Comment


def init_driver_firefox():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("http.response.timeout", 10)
    firefox_profile.set_preference("dom.max_script_run_time", 10)
    firefox_profile.set_preference("webdriver.load.strategy", "unstable")
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.wait = WebDriverWait(driver, 20)
    driver.set_page_load_timeout(10)
    return driver


def standaard_scrape(task_id, search_word, driver, start_date, end_date):
    """
    Scrapes the archive of the newspaper The Standaard
    Fetches social media content
    http://www.standaard.be/zoeken?keyword=
    :param task_id: Task id generated by Celery
    :param start_date: The startDate of the search
    :param end_date: The end date of the search
    """
    logger = logging.getLogger('newsscraper')
    delay = 3
    example_url = "http://www.standaard.be/zoeken?keyword=test&datestart=01%2F03%2F2016&dateend=23%2F03%2F2016&categoryrange=00000000-0000-0000-0000-000000000000"
    firstpart_url = "http://www.standaard.be/zoeken?keyword="
    startdate_url = "&datestart="
    enddate_url = "&dateend="
    lastpart_url = "&categoryrange=00000000-0000-0000-0000-000000000000"
    start_date = start_date.replace('/', "%2F")
    end_date = end_date.replace('/', "%2F")
    total_url = firstpart_url + search_word + startdate_url + start_date + enddate_url + end_date + lastpart_url

    # on the first page, the &page=<number> must not be added to the search url
    retry_loop = True
    result_page = 1
    # continue to loop until links to articles are found
    while retry_loop:
        logger.debug("Start loop, page= " + str(result_page))
        if result_page == 2:
            # add the page parameter to the string starting from iteration 2
            total_url += "&page=" + str(result_page)
        if result_page > 2:
            # replace the last number in the string starting from the third iteration
            total_url = total_url[:-1] + str(result_page)
        logger.debug("total url: " + total_url)
        try:
            driver.get(total_url)
        except TimeoutException:
            pass
        '''
        try:
            WebDriverWait(driver, delay).until()
        except TimeoutException:
            logger.debug("loading took too long")
        '''
        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all("article")
        # retry the loop while the &pages=<number> gives back results
        results = False
        for article in articles:
            time.sleep(1)
            # all links in articles on the page
            for a in article.findAll("a"):
                article_url = a.get("href")
                # if the link contains 'cnt', it's a link to an complete article
                if 'cnt' in article_url:
                    results = True
                    # open the page of the article and fetch information
                    article_to_save = Article()
                    article_to_save.task_id = task_id
                    article_to_save.newspaper = "Standaard"
                    article_to_save.hyperlink = article_url
                    try:
                        driver.get(article_url)
                    except TimeoutException as e:
                        logger.debug(e)
                        continue
                    time.sleep(2)
                    soup_art = BeautifulSoup(driver.page_source, "html.parser")
                    # paying articles has title meta in header without a class
                    headers = soup_art.find_all("header")
                    for header in headers:
                        # the title of the paying article is in a h1 with class of article__header
                        for h1 in header.find_all("h1", class_="article__header"):
                            # only paying articles have this
                            article_to_save.free_article = False
                            title_text = re.sub(r"\s+", " ", h1.get_text())
                            article_to_save.title = title_text
                        for small in header.find_all("small", class_="article__content-info"):
                            # date of paying article in time tag
                            for t in small.find_all("time"):
                                article_time = re.sub(r"\s+", " ", t.get_text())
                                article_to_save.date = article_time
                            # author is sometimes in an element within the small
                            author = None
                            for a in small.find_all("a"):
                                author = a.get_text()
                            # sometimes the author is the text of the small
                            if not author:
                                text_small = small.get_text()
                                if text_small:
                                    # this text has to be cleaned still
                                    author = text_small[text_small.find("|")+1:].strip()
                            article_to_save.author = author
                            # free articles have title meta in header with class article__meta
                    headers_title = soup_art.find_all("header", class_='article__header')
                    for header_title in headers_title:
                        for h1 in header_title.find_all("h1", {"itemprop":"name"}):
                            article_to_save.title = h1.get_text()

                    date_author_source_data = soup_art.find_all("footer", class_='article__meta')
                    for footer in date_author_source_data:
                        article_to_save.free_article = True
                        for t in footer.find_all("time"):
                            article_to_save.date = t.get_text()
                        for a in footer.find_all("span", {'itemprop':'author'}):
                            article_to_save.author = a.get_text()
                        for s in footer.find_all("span", {'itemprop': 'sourceOrganization'}):
                            source_text = re.sub(r"\s+", " ", s.get_text())
                            source_text = source_text.strip('\n\r\t')
                            article_to_save.source = source_text
                    # Facebook likes with selenium can be found on site
                    for div in soup_art.find_all("div", class_="social  social--large"):
                        if div["data-social"] == "googleplus":
                            article_to_save.googleplus_shares = div["data-shares"]
                        if div["data-social"] == "twitter":
                            article_to_save.twitter_shares = div["data-shares"]
                        if div["data-social"] == "facebook":
                            article_to_save.facebook_shares = div["data-shares"]

                    # embedded tweets
                    iframes_twitter = driver.find_elements_by_class_name("twitter-tweet-rendered")
                    tweets_list = list()
                    for iframe in iframes_twitter:
                        try:
                            driver.switch_to_frame(iframe)
                            frame_soup = BeautifulSoup(driver.page_source, "html.parser")
                            tweet_blockquotes = frame_soup.find_all("blockquote", class_="Tweet")

                            for tweet_blockquote in tweet_blockquotes:
                                tweet = EmbeddedTweet()
                                for p in tweet_blockquote.find_all("p"):
                                    tweet.lang = p['lang']
                                    tweet.text = p.get_text()
                                    # save links and hashtags
                                    hashtags = ""
                                    links = ""
                                    for a_link in p.find_all("a"):
                                        if "src=hash" in a_link["href"]:
                                            # hashtag if it contains "src=hash"
                                            hashtags += a_link.get_text() + ","
                                        else:
                                            # it's a link
                                            links += a_link.get_text() + ","
                                    tweet.hashtags = hashtags.strip(",")
                                    tweet.links = links.strip(",")
                                for a_link in tweet_blockquote.find_all("a"):
                                    # fetch only the tweet status links
                                    if "/status/" in a_link["href"]:
                                        tweet.twitter_link = a_link["href"]

                                # the tweeter name and date are in the blockquote text
                                # note: split on long stripe
                                tweeter_name_and_date = tweet_blockquote.get_text().split(u'\u2014')[-1]
                                tweet.author = tweeter_name_and_date[tweeter_name_and_date.find("(")+1:tweeter_name_and_date.find(")")]
                                tweet.date = tweeter_name_and_date[tweeter_name_and_date.find(")")+1:].strip()
                                tweets_list.append(tweet)
                            driver.switch_to_default_content()
                        except (NoSuchFrameException, StaleElementReferenceException) as e:
                            logger.debug(e)
                            # pin its are in figures with class pin-container
                    for figure in soup_art.find_all("figure", class_="pin-container"):
                        for img in figure.find_all("img"):
                            try:
                                # link of the pin it image is in src tag
                                article_to_save.pin_it = img["src"]
                            except:
                                pass
                    #link to video
                    for div in soup_art.find_all("div", {"id":"VIDSW_title-ds"}):
                        for a in div.find_all("a"):
                            article_to_save.video += a["href"] + ","

                    # sometimes a link to a tweet is embedded in a button on a video
                    # NOTE: a button inside an iframe is very tricky
                    '''
                    for twitter_button_link in soup_art.find_all("div", {"class":"twitter-button-container"}):
                        tweet = EmbeddedTweet()
                        logger.debug(twitter_button_link["href"])
                        tweet.twitter_link = twitter_button_link["href"]
                    '''
                    article_to_save.save()
                    for tweet in tweets_list:
                        tweet.article = article_to_save
                        tweet.save()

        logger.debug("end of loop")
        result_page += 1
        if not results:
            retry_loop = False


def hln_scrape(task_id, search_word, driver, start_date, end_date):
    """
    An archive search on The Standaard is executed with always the same URL in the form of
    http://www.standaard.be/zoeken?keyword=<keyword>&datestart=<startdate>&dateend=<enddate>
    &categoryrange=00000000-0000-0000-0000-000000000000
    If there are more results &page=<number> is added
    if no results, the search is stopped
    """
    logger = logging.getLogger('newsscraper')
    # delay for selenium webrowserwait
    delay = 3
    example_url = "http://www.hln.be/hln/nl/1/article/search.dhtml?searchValue=terpstra&resultAmountPerPage=&page=0&startSearchDate=01042016&endSearchDate=04042016&filterNavigationItemId=&filterSource=&timeFilter=specific"

    firstpart_url = "http://www.hln.be/hln/nl/1/article/search.dhtml?searchValue="
    # result amount starts empty, after first page = 10
    result_amount_url = "&resultAmountPerPage="
    # page starts at 0
    page_part_url = "&page="
    startdate_url = "&startSearchDate="
    enddate_url = "&endSearchDate="
    lastpart_url = "&filterNavigationItemId=&filterSource=&timeFilter=specific"
    # url attachment for comments
    comments_url = "?show=react"
    start_date = start_date.replace('/', '')
    end_date = end_date.replace('/', '')
    page = 0
    amount_per_page = None
    retry_loop = True
    # page count +1 at iteration
    while retry_loop:
        # if no results are returned, the loop must stop
        # TODO: sometimes error: websites is not available

        retry_loop = False
        if amount_per_page is None:
            total_url = firstpart_url + search_word + result_amount_url + page_part_url + str(page) + startdate_url + start_date + enddate_url + end_date +  lastpart_url
        else:
            total_url = firstpart_url + search_word + result_amount_url + str(amount_per_page) + page_part_url + str(page) + startdate_url + start_date + enddate_url + end_date + result_amount_url + lastpart_url
        logger.debug("total url: " + total_url)
        try:
            driver.get(total_url)
        except TimeoutException:
            pass
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # all article links are in the div searchResultBox
        for search_results in soup.find_all("div", {"id": "searchResultBox"}):
            # iterate over articles
            for link in search_results.find_all("a"):
                # exclude the search.dhtml links                
                if "search.dhtml?" not in link["href"]:
                    # results are found, continue the loop
                    retry_loop = True
                    article_url = "http://www.hln.be" + link["href"]
                    logger.debug("* link = " + article_url)
                    # open the article with the link and download the data
                    try:
                        driver.get(article_url)
                    except TimeoutException:
                        logger.debug("timeoutexception")
                        pass
                    time.sleep(3)
                    art_soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Start new article
                    article_to_save = Article()
                    article_to_save.task_id = task_id
                    article_to_save.hyperlink = article_url

                    # find facebook shares with facebook graph, span with number doesn't show up
                    facebook_url = "http://graph.facebook.com/?id="
                    total_url = facebook_url + article_url
                    request_facebook_graph = requests.get(total_url)
                    facebook_soup = BeautifulSoup(request_facebook_graph.content, "html.parser")
                    facebook_data = json.loads(str(facebook_soup))
                    try:
                        article_to_save.facebook_shares = str(facebook_data['shares'])
                    except:
                        pass

                    # instagram pictures are inside iframes, driver must switch to the iframe to fetch them
                    iframes = driver.find_elements_by_class_name("embedly-card")
                    instagram_links = ""
                    for iframe in iframes:
                        try:
                            driver.switch_to_frame(iframe)
                            frame_soup = BeautifulSoup(driver.page_source, "html.parser")
                            for a in frame_soup.find_all("a"):
                                # multiple links are returned, take only those that are instagram pics
                                if "www.instagram.com/p/" in a["href"]:
                                    instagram_links += a["href"] + ","
                            # driver must switch back to default content, otherwise error
                            driver.switch_to.default_content()
                        except (NoSuchFrameException, StaleElementReferenceException):
                            pass
                    article_to_save.instagram_links = instagram_links

                    # embedded tweets are into iframes, driver must switch to the iframe
                    iframes_twitter = driver.find_elements_by_class_name("twitter-tweet")
                    tweets_list = list()
                    for iframe in iframes_twitter:
                        try:
                            tweet = EmbeddedTweet()
                            driver.switch_to_frame(iframe)
                            frame_soup = BeautifulSoup(driver.page_source, "html.parser")
                            for blockquote in frame_soup.find_all("blockquote"):
                                tweet.twitter_link = blockquote['cite']
                                for a in blockquote.find_all("a", class_="TweetAuthor-link Identity u-linkBlend"):
                                    tweet.author = a['aria-label']
                                for p in blockquote.find_all("p"):
                                    # the text contains all text with hashtags
                                    tweet.text = p.get_text()
                                    # hashtags are actually inside <a>, store separately
                                    for hashtag_link in p.find_all("a", class_="PrettyLink hashtag customisable"):
                                        hashtag = ""
                                        for span in hashtag_link.find_all("span"):
                                            hashtag += span.get_text()
                                        tweet.hashtags += hashtag + ","
                                for a in blockquote.find_all("a", class_="u-linkBlend u-url customisable-highlight long-permalink"):
                                    tweet.date = a["data-datetime"]
                                for a in blockquote.find_all("a", class_="PrettyLink link media customisable"):
                                    tweet.links += a.get_text() + ','
                            logger.debug(tweet)
                            tweets_list.append(tweet)
                            # return to default content for next iteration, otherwise error is thrown
                            driver.switch_to_default_content()
                        except (NoSuchFrameException, StaleElementReferenceException) as e:
                            logger.debug(e)

                    # fetch comments
                    comments_list = list()
                    total_comments_url = article_url + comments_url
                    try:
                        driver.get(total_comments_url)
                    except TimeoutException:
                        logger.debug("timeoutexception")
                        pass
                    comments_soup = BeautifulSoup(driver.page_source, "html.parser")
                    # get the comments of the first page
                    for section in comments_soup.find_all("section", {"id":"reaction"}):
                        for li in section.find_all("li"):
                            comment_to_save = Comment()
                            for cite in li.find("cite"):
                                # sometimes cite is only name, sometimes name with  
                                comment_to_save.author = re.sub('\s+', ' ', cite).strip()
                            for blockquote in li.find("blockquote"):
                                comment_to_save.text = blockquote.strip()
                            for time_comment in li.find("span"):
                                comment_to_save.date = time_comment.strip()
                            comments_list.append(comment_to_save)
                            logger.debug(comment_to_save)


                    # comments are in multiple pages with link "volgende"
                    # now fetching comments of the next pages
                    # find the link with xpath and click it with selenium
                    new_comments_exist = True
                    first_iteration = True
                    while new_comments_exist:
                        # if a cookie banner exists, click on the button continue, otherwise an error is thrown
                        try:
                            button = driver.find_element_by_class_name('fjs-cookie-banner-button')
                            button.click()
                        except (NoSuchElementException, ElementNotVisibleException):
                            logger.debug("no banner")
                            pass
                        try:
                            # first time xpath is //*[@id="reaction"]/div[1]/a
                            # second time xpath is //*[@id="reaction"]/div[1]/a[2]
                            if first_iteration:
                                link = driver.find_element_by_xpath('//*[@id="reaction"]/div[1]/a')
                                driver.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reaction"]/div[1]/a')))
                                first_iteration = False
                            else:
                                link = driver.find_element_by_xpath('//*[@id="reaction"]/div[1]/a[2]')
                                driver.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="reaction"]/div[1]/a[2]')))

                            link.click()
                            time.sleep(2)
                            comments_followup_soup = BeautifulSoup(driver.page_source, "html.parser")
                            for section in comments_followup_soup.find_all("section", {"id":"reaction"}):
                                for li in section.find_all("li"):
                                    comment_to_save = Comment()
                                    for cite in li.find("cite"):
                                        # sometimes cite is only name, sometimes name with  
                                        comment_to_save.author = re.sub('\s+', ' ', cite).strip()
                                    for blockquote in li.find("blockquote"):
                                        comment_to_save.text = blockquote.strip()
                                    for time_comment in li.find("span"):
                                        comment_to_save.date = time_comment.strip()
                                    comments_list.append(comment_to_save)
                                    logger.debug(comment_to_save)
                        except NoSuchElementException:
                            logger.debug("No more comments")
                            new_comments_exist = False
                        time.sleep(1)

                    logger.debug(article_to_save)
                    time.sleep(1)
        page += 1
        amount_per_page = 10
    logger.debug("loop stopped")