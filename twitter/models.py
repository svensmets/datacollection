from django.contrib.auth.models import User
from django.db import models
from djcelery.models import TaskState


# http://stackoverflow.com/questions/1372016/django-models-custom-functions
class TaskManager(models.Manager):
    """
    This class helps to get the tasks of a user
    """
    def get_tasks_of_user(self, user):
        """
        method returns all SearchTasks of the user in the database
        """
        tasks = []
        search_tasks = self.filter(user=user)
        for search_task in search_tasks:
            try:
                full_task = TaskState.objects.get(task_id=search_task.task)
                tasks.append("Name: " + full_task.name + " Status: " + full_task.state +
                             " Date: " + full_task.tstamp.strftime("%Y-%m-%d %H:%M:%S"))
            except TaskState.DoesNotExist:
                pass
        return tasks

    def get_task_of_user_in_string_format(self, user):
        """
        method returns all SearchTasks of the user in string format
        """
        tasks = []
        search_tasks = self.filter(user=user)
        for search_task in search_tasks:
            try:
                full_task = TaskState.objects.get(task_id=search_task.task)
                tasks.append("Name: " + full_task.name + " Status: " + full_task.state + " Date: " +
                             full_task.tstamp.strftime("%Y-%m-%d %H:%M:%S"))
            except TaskState.DoesNotExist:
                # exception needed: the last task does not yet exist when the user enters a search task
                # and the homescreen is called with the redirect from profile_information_search
                # solution: refresh with ajax call from template
                # http://stackoverflow.com/questions/11539152/django-matching-query-does-not-exist-after-object-save-in-celery-task
                pass
        return tasks

    def get_tasks_of_user_delimited(self, user):
        """
        returns the taks of the user delimited with a ';'
        """
        tasks = []
        search_tasks = self.filter(user=user)
        for search_task in search_tasks:
            try:
                full_task = TaskState.objects.get(task_id=search_task.task)
                tasks.append("Name: " + full_task.name + " Status: " + full_task.state + " Date: "
                             + full_task.tstamp.strftime("%Y-%m-%d %H:%M:%S") + ";")
            except TaskState.DoesNotExist:
                # exception needed: the last task does not yet exist when the user enters a search task
                # and the homescreen is called with the redirect from profile_information_search
                # solution: refresh with ajax call from template
                # http://stackoverflow.com/questions/11539152/django-matching-query-does-not-exist-after-object-save-in-celery-task
                pass
        return tasks


class SearchTask(models.Model):
    """
    Represents a search task the user has initiated
    All searchtasks are shown on the homescreenpage
    """
    user = models.ForeignKey(User, null=True)
    task = models.CharField(max_length=250, null=True)
    objects = TaskManager()


class TwitterUser(models.Model):
    """
    Represents a User of Twitter, not a user of the program
    User of the program is represented by built in User class
    """
    user_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=100)
    friends_count = models.BigIntegerField()
    followers_count = models.BigIntegerField()
    # protected accounts cannot be accessed
    is_protected = models.BooleanField(default=False)
    # when the twitteruser has too many followers, account is ignored
    max_followers_exceeded = models.BooleanField(default=False)
    # date_added = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=250)


class TwitterList(models.Model):
    """
    Represents a list in twitter
    A twitter_user can be a member of a list or a subscriber
    """
    list_id = models.BigIntegerField(primary_key=True)
    list_name = models.CharField(max_length=200)
    list_full_name = models.CharField(max_length=200)
    user_membership = models.ManyToManyField(TwitterUser, related_name="list_membership", blank=True)
    user_subscription = models.ManyToManyField(TwitterUser, related_name="list_subscription", blank=True)
    task_id = models.CharField(max_length=250)


class Tweet(models.Model):
    """
    Represents a tweet in twitter
    """
    tweet_id = models.BigIntegerField(primary_key=True)
    tweeter_id = models.BigIntegerField()
    tweeter_name = models.CharField(max_length=200)
    tweet_text = models.CharField(max_length=200)
    tweet_date = models.DateTimeField()
    is_retweet = models.BooleanField()
    mentions = models.CharField(max_length=200, blank=True)
    hashtags = models.CharField(max_length=200, blank=True)
    hyperlinks = models.CharField(max_length=200, blank=True)
    task_id = models.CharField(max_length=250)


class TwitterKeys(models.Model):
    """
    The keys the user enters into the application to start a search
    """
    consumer_key = models.CharField(max_length=200)
    consumer_secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    access_token_secret = models.CharField(max_length=200)
    user = models.ForeignKey(User)


class TwitterRelationship(models.Model):
    """
    Relationship between two Twitter Users
    """
    from_user_id = models.BigIntegerField()
    to_user_id = models.BigIntegerField()
    relation_used = models.CharField(max_length=100)
