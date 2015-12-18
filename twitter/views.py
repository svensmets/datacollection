from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from twitter.forms import NamesTextAreaForm
from twitter.forms import SearchOptionsForm
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from twitter.models import SearchTask
from twitter.tweepy import TwitterTweepy
from twitter.tasks import profile_information_search_task


class HomescreenPage(TemplateView):
    """
    Page shows the current tasks the user has running and show options to start a search
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = request.user
        tasks = SearchTask.objects.get_task_of_user_in_string_format(user)
        add_names_form = NamesTextAreaForm
        all_names_form = NamesTextAreaForm
        search_options_form = SearchOptionsForm
        return render(request, "twitter/homescreen.html", {'tasks': tasks, 'add_names_form': add_names_form,
                                                           'all_names_form': all_names_form,
                                                           'search_options_form': search_options_form})

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        tasks = SearchTask.objects.get_task_of_user_in_string_format(user)
        return render(request, "twitter/homescreen.html", {'tasks': tasks})


def lookupname(request):
    """
    Checks whether a name is a valid username or not
    Responds to ajax call in homescreen
    After button add name is clicked
    :param request: contains name to check
    :return: true if valid username, false if not
    """
    if request.method == 'GET':
        name = request.GET.get('name', '')
        twitter = TwitterTweepy()
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
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            names = body['names']
            followers = body['followers']
            friends = body['friends']
            max_followers = body['maxfollowers']
            list_memberships = body['listmemberships']
            list_subscriptions = body['listsubscriptions']
            # start search task
            params = {'friends': friends, 'followers': followers, 'max_followers': max_followers,
                      'list_memberships': list_memberships, 'list_subscriptions': list_subscriptions}
            status = profile_information_search_task.delay(names, **params)
            # bind task to user and store in db
            search_task = SearchTask(user=request.user, task=status.task_id)
            search_task.save()
            return HttpResponseRedirect('/homescreen/')

def tweets_by_name_search(request):
    """
    Start a streaming search of tweets based on a list of names
    :param request:
    names = list of names for the filter in the search
    :return:
    """