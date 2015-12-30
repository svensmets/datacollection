from django import template
from django.core.exceptions import ObjectDoesNotExist
from twitter.models import TwitterKeys
from django.contrib.auth.models import User
register = template.Library()


@register.filter(name='addcss')
def add_css(field, css):
    """
    filter to add css in template to fields in forms
    otherwise the css would have to be added in form definition
    usage: {{field|addcss:"form-control"}} in template
    http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
    :param field: the field to add the css to
    :param css: the css that has to be added to the field
    :return the field with css added to it
    """
    return field.as_widget(attrs={"class": css})


def get_twitter_keys(user):
    """
    Checks if a user has entered valid auth keys
    :param user: datacollection user object
    :return: Keys if user has valid keys, false if not
    """
    try:
        keys = TwitterKeys.objects.get(user=user)
        return keys
    except ObjectDoesNotExist:
        return False


def get_twitter_keys_with_user_id(user_id):
    """
    Returns the keys from the user with the id
    Needed for the Celery tasks (user or keys not serializable)
    :param user_id:
    :return: the keys of the user with the specified user_id, false if user or keys not found
    """
    try:
        user = User.objects.get(id=user_id)
        keys = get_twitter_keys(user)
        return keys
    except ObjectDoesNotExist:
        return False

