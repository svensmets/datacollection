from django import template
from django.core.exceptions import ObjectDoesNotExist
from djcelery.models import TaskState
from twitter.models import TwitterKeys, SearchTask
from django.contrib.auth.models import User
import os
import zipfile
import logging
from django.contrib.auth.decorators import user_passes_test
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


def has_running_task(user):
    """
    Checks if a user has a task running
    :param user: the user to check
    :return: True if user has a task running, False if not
    """
    # note: raw query must include primary key, otherwise an error is thrown
    tasks = TaskState.objects.raw("SELECT dj.id, dj.task_id, dj.name FROM djcelery_taskstate dj INNER JOIN twitter_searchtask twit "
                                 "ON dj.task_id = twit.task WHERE (dj.state LIKE {0} OR dj.state LIKE {1}) "
                                 "AND twit.user_id = {2} LIMIT 1".format("'STARTED'", "'RECEIVED'", user.id));
    # if tasks contains a task: the user has a task running, if no taks, return false
    for task in tasks:
        return True
    return False


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


def not_guest(function=None):
    """
    Used in views to prevent guest users from doing certain searches
    https://gist.github.com/bradmontgomery/5657267
    (27/02/2016)
    :param function:
    :return:
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and not u.groups.filter(name='guest').exists()
    )
    return actual_decorator(function)


def zip_directory(path, task_id):
    """
    Zips the directory in the path
    # http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    (25/02/2016)
    :param path: the path of the directory
    :return:
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

# code starting from here was copied from djqscsv.py
# code had to be changed (slightly) to be able to use it for python 3
# ex: unicode existed in python 2 but was changed to str in python 3

import csv
import datetime
from djqscsv import CSVException
from django.utils import six


# Keyword arguments that will be used by this module
# the rest will be passed along to the csv writer
DJQSCSV_KWARGS = {'field_header_map': None,
                  'field_serializer_map': None,
                  'use_verbose_names': True,
                  'field_order': None}


def write_csv(queryset, file_obj, **kwargs):
    """
    The main worker function. Writes CSV data to a file object based on the
    contents of the queryset.
    """

    # process keyword arguments to pull out the ones used by this function
    field_header_map = kwargs.get('field_header_map', {})
    field_serializer_map = kwargs.get('field_serializer_map', {})
    use_verbose_names = kwargs.get('use_verbose_names', True)
    field_order = kwargs.get('field_order', None)

    csv_kwargs = {}

    for key, val in six.iteritems(kwargs):
        if key not in DJQSCSV_KWARGS:
            csv_kwargs[key] = val

    # add BOM to support CSVs in MS Excel (for Windows only)
    file_obj.write(_safe_utf8_stringify(u'\ufeff'))

    # the CSV must always be built from a values queryset
    # in order to introspect the necessary fields.
    # However, repeated calls to values can expose fields that were not
    # present in the original qs. If using `values` as a way to
    # scope field permissions, this is unacceptable. The solution
    # is to make sure values is called *once*.

    # perform an string check to avoid a non-existent class in certain
    # versions
    if type(queryset).__name__ == 'ValuesQuerySet':
        values_qs = queryset
    else:
        # could be a non-values qs, or could be django 1.9+
        iterable_class = getattr(queryset, '_iterable_class', object)
        if iterable_class.__name__ == 'ValuesIterable':
            values_qs = queryset
        else:
            values_qs = queryset.values()

    try:
        field_names = values_qs.query.values_select
    except AttributeError:
        try:
            field_names = values_qs.field_names
        except AttributeError:
            # in django1.5, empty querysets trigger
            # this exception, but not django 1.6
            raise CSVException("Empty queryset provided to exporter.")

    extra_columns = list(values_qs.query.extra_select)
    if extra_columns:
        field_names += extra_columns

    try:
        aggregate_columns = list(values_qs.query.annotation_select)
    except AttributeError:
        # this gets a deprecation warning in django 1.9 but is
        # required in django<=1.7
        aggregate_columns = list(values_qs.query.aggregate_select)

    if aggregate_columns:
        field_names += aggregate_columns

    if field_order:
        # go through the field_names and put the ones
        # that appear in the ordering list first
        field_names = ([field for field in field_order
                        if field in field_names] +
                       [field for field in field_names
                        if field not in field_order])

    writer = csv.DictWriter(file_obj, field_names, **csv_kwargs)

    # verbose_name defaults to the raw field name, so in either case
    # this will produce a complete mapping of field names to column names
    name_map = dict((field, field) for field in field_names)
    if use_verbose_names:
        name_map.update(
            dict((field.name, field.verbose_name)
                 for field in queryset.model._meta.fields
                 if field.name in field_names))

    # merge the custom field headers into the verbose/raw defaults, if provided
    merged_header_map = name_map.copy()
    if extra_columns:
        merged_header_map.update(dict((k, k) for k in extra_columns))
    merged_header_map.update(field_header_map)

    merged_header_map = dict((k, _safe_utf8_stringify(v))
                             for (k, v) in merged_header_map.items())
    writer.writerow(merged_header_map)

    for record in values_qs:
        record = _sanitize_unicode_record(field_serializer_map, record)
        writer.writerow(record)


########################################
# utility functions
########################################


def _safe_utf8_stringify(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, str):
        return value.encode('utf-8')
    else:
        return value


def _sanitize_unicode_record(field_serializer_map, record):

    def _serialize_value(value):
        # provide default serializer for the case when
        # non text values get sent without a serializer
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        else:
            return value

    obj = {}
    for key, val in six.iteritems(record):
        if val is not None:
            serializer = field_serializer_map.get(key, _serialize_value)
            newval = serializer(val)
            obj[_safe_utf8_stringify(key)] = _safe_utf8_stringify(newval)

    return obj