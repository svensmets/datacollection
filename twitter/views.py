import email
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, HttpResponseRedirect
from twitter.forms import NamesTextAreaForm, SearchOptionsForm, AddTwitterKeysForm
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from twitter.models import SearchTask, TwitterKeys
from twitter.tweepy import TwitterTweepy
from twitter.tasks import profile_information_search_task
from twitter.tasks import start_tweets_by_name_streaming
from twitter.tasks import start_tweets_searchterms_streaming
from twitter.tasks import start_tweets_searchterms_searchapi
from twitter.tasks import start_tweets_names_searchapi
from twitter.util import get_twitter_keys
from tweepy import TweepError
import logging


class HomescreenPage(TemplateView):
    """
    Page shows the current tasks the user has running and show options to start a search
    """

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = request.user
        keys = get_twitter_keys(user)
        if keys is False:
            return HttpResponseRedirect('/addkeys/')
        else:
            tasks = SearchTask.objects.get_tasks_of_user(user=user)
            add_names_form = NamesTextAreaForm
            all_names_form = NamesTextAreaForm
            search_options_form = SearchOptionsForm
            return render(request, "twitter/homescreen.html", {'tasks': tasks, 'add_names_form': add_names_form,
                                                               'all_names_form': all_names_form,
                                                               'search_options_form': search_options_form})

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        tasks = SearchTask.objects.get_tasks_of_user(user=user)
        return render(request, "twitter/homescreen.html", {'tasks': tasks})


class AddTwitterKeys(View):
    """
    Shows the page to add keys to the database
    """

    @method_decorator(login_required)
    def get(self, request):
        add_keys_form = AddTwitterKeysForm
        return render(request, "twitter/addkeys.html", {'add_keys_form': add_keys_form})

    @method_decorator(login_required)
    def post(self, request):
        form = AddTwitterKeysForm(request.POST)
        user = request.user
        if form.is_valid():
            consumer_key = form.cleaned_data['consumer_key']
            consumer_secret = form.cleaned_data['consumer_secret']
            access_token = form.cleaned_data['access_token']
            access_token_secret = form.cleaned_data['access_token_secret']
            keys_to_insert = {consumer_key: consumer_key, consumer_secret: consumer_secret, access_token: access_token,
                              access_token_secret: access_token_secret}
            keys = TwitterKeys(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token,
                               access_token_secret=access_token_secret, user=user)
            try:
                # test validity keys
                TwitterTweepy(keys)
                # save if keys valid, or update if already keys in database
                try:
                    db_keys = TwitterKeys.objects.get(user_id=user.id)
                    db_keys.consumer_key = consumer_key
                    db_keys.consumer_secret = consumer_secret
                    db_keys.access_token = access_token
                    db_keys.access_token_secret = access_token_secret
                    db_keys.save()
                except TwitterKeys.DoesNotExist:
                    keys.save()
                TwitterKeys.objects.update_or_create(user=user, defaults=keys_to_insert)
                return render(request, 'twitter/homescreen.html')
            except TweepError:
                return render(request, 'twitter/addkeys.html',
                              {'error_message': 'Keys is not valid', 'add_keys_form': form})
        else:
            return render(request, 'twitter/addkeys.html',
                          {'error_message': 'Form is not valid', 'add_keys_form': form})


def lookupname(request):
    """
    Checks whether a name is a valid username or not
    Responds to ajax call in homescreen
    After button add name is clicked
    :param request: contains name to check
    :return: true if valid username, false if not
    """
    if request.method == 'GET':
        logger = logging.getLogger(__name__)
        logger.debug("look up name")
        user = request.user
        keys = get_twitter_keys(user)
        if keys is False:
            return HttpResponseRedirect('/addkeys/')
        else:
            name = request.GET.get('name', '')
            twitter = TwitterTweepy(keys)
            if twitter.user_exists(name):
                return HttpResponse(json.dumps({'exists': 'true'}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'exists': 'false'}), content_type='application/json')


def get_tasks(request):
    """
    returns all tasks when a user clicks the refresh button on the homescreen
    :param request:
    :return: user and tasks of the user
    """
    if request.method == 'POST':
        user = request.user
        tasks = SearchTask.objects.get_tasks_of_user_delimited(user)
        data = {'user': user.username, 'tasks': tasks}
        return HttpResponse(json.dumps(data), content_type='application/json')


def profile_information_search(request):
    """
    Starts a task: search of profile information
    Responds to ajax call in homescreen
    :param request:
        maxfollowers = maximum number of followers twitteruser(s) may have
        friends = lookup friends of twitteruser(s)
        follower = lookup friends of twitteruser(s)
    :return:
    """
    if request.is_ajax():
        if request.method == 'POST':
            # http://stackoverflow.com/questions/29780060/trying-to-parse-request-body-from-post-in-django
            # json.loads() only accepts a unicode string, so it must be decoded before passing it to json.loads()
            logger = logging.getLogger(__name__)
            logger.debug("profile information search")
            user = request.user
            keys = get_twitter_keys(user)
            if keys is False:
                return HttpResponseRedirect('/addkeys/')
            else:
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                names = body['names']
                followers = body['followers']
                friends = body['friends']
                max_followers = body['maxfollowers']
                list_memberships = body['listmemberships']
                list_subscriptions = body['listsubscriptions']
                relationships_checked = body['relationshipschecked']
                # start search task
                params = {'friends': friends, 'followers': followers, 'max_followers': max_followers,
                          'list_memberships': list_memberships, 'list_subscriptions': list_subscriptions,
                          'relationships_checked': relationships_checked}
                # user id param necessary because user or keys not serializable
                status = profile_information_search_task.delay(names=names, user_id=user.id, email=user.email, **params)
                # bind task to user and store in db
                search_task = SearchTask(user=request.user, task=status.task_id)
                search_task.save()
                return HttpResponseRedirect('/homescreen/')


def tweets_by_name_search(request):
    """
    Start a streaming search of tweets based on a list of names
    Start a search api search of tweets seven days in the past
    :param request:
    names = list of names for the filter in the search
    :return:
    """
    if request.is_ajax():
        if request.method == 'POST':
            logger = logging.getLogger(__name__)
            user = request.user
            keys = get_twitter_keys(user)
            if keys is False:
                return HttpResponseRedirect('/addkeys/')
            else:
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                names = body['names']
                search_api_tweets = body['getSearchApiTweets']
                streaming_tweets = body['getStreamingTweets']
                nr_of_days = body['nrOfDays']
                logger.debug("Search api " + str(search_api_tweets))
                email_addr = user.email
                if search_api_tweets:
                    names_list = str.split(names, ',')
                    # user id param necessary because user or keys not serializable
                    status = start_tweets_names_searchapi.delay(names_list=names_list, user_id=user.id, email=email_addr)
                    # bind task to user and store in db
                    search_task = SearchTask(user=request.user, task=status.task_id)
                    search_task.save()
                logger.debug("Streaming " + str(streaming_tweets))
                # transform names list in userIds
                # the names must be in a list for the lookup_users method
                if streaming_tweets:
                    names_list = str.split(names, ',')
                    tweepy = TwitterTweepy(keys=keys)
                    # first get the ids of the screenames
                    ids = tweepy.get_ids_from_screennames(names_list)
                    logger.debug("ids count= " + str(len(ids)))
                    # note: to avoid error: changes to streaming.py in tweepy code was made
                    # https://github.com/tweepy/tweepy/issues/615
                    # user id param necessary because user or keys not serializable
                    status = start_tweets_by_name_streaming.delay(user_ids=ids, user_id=user.id, nr_of_days=nr_of_days,
                                                         email=email_addr)
                    # bind task to user and store in db
                    search_task = SearchTask(user=request.user, task=status.task_id)
                    search_task.save()
                return HttpResponseRedirect('/homescreen')


def tweets_by_searchterm_search(request):
    """
    Start a streaming search of tweets based on a list of comma
    separated serach terms
    start a search api search of tweets seven days in the past
    :param request:
    :return:
    """
    if request.is_ajax():
        if request.method == 'POST':
            logger = logging.getLogger(__name__)
            user = request.user
            keys = get_twitter_keys(user)
            if keys is False:
                return HttpResponseRedirect('/addkeys/')
            else:
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                searchterms = body['searchTerms']
                search_api_tweets = body['getSearchApiTweets']
                streaming_tweets = body['getStreamingTweets']
                nr_of_days = body['nrOfDays']
                email_addr = user.email
                searchterm_list = str.split(searchterms, ',')
                logger.debug("Streaming " + str(streaming_tweets))
                if search_api_tweets:
                    # user id param necessary because user or keys not serializable
                    status = start_tweets_searchterms_searchapi.delay(searchterms=searchterm_list, user_id=user.id,
                                                                      email=email_addr)
                    # bind task to user and store in db
                    search_task = SearchTask(user=request.user, task=status.task_id)
                    search_task.save()
                if streaming_tweets:
                    # user id param necessary because user or keys not serializable
                    status = start_tweets_searchterms_streaming.delay(searchterms=searchterm_list, user_id=user.id,
                                                             nr_of_days=nr_of_days, email=email_addr)
                    # bind task to user and store in db
                    search_task = SearchTask(user=request.user, task=status.task_id)
                    search_task.save()
                return HttpResponseRedirect('/homescreen')


def get_task_data(request):
    """
    http://www.azavea.com/blogs/labs/2014/03/exporting-django-querysets-to-csv/
    https://github.com/johnsensible/django-sendfile
    (access on 01/02/2016)
    :param request:
    :return:
    """
    if request.method == 'POST':
        user = request.user
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        names = body['names']


