from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sendfile import sendfile
from newsscraper.forms import NewssiteArchiveSearchForm
import logging
from newsscraper.models import ScrapeTask
from newsscraper.serializers import ScrapeTaskSerializer
from newsscraper.tasks import standaard_archive_scrape, hln_archive_scrape
from djcelery.models import TaskState
import dateutil.parser


class NewsScraperView(TemplateView):

    template_name = 'newsscraper/newsscraper.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewsScraperView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsScraperView, self).get_context_data(**kwargs)
        context.update(form_archive_search=NewssiteArchiveSearchForm(form_name='search_archive_form'))
        return context


@api_view(['GET'])
def task_list(request):
    """
    List tasks of a user
    :param request:
    """
    if request.method == 'GET':
        user = request.user
        tasks = ScrapeTask.objects.filter(user=user)
        if tasks:
            serializer = ScrapeTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        else:
            return Response()


def start_archive_search(request):
    if request.method == 'POST':
        user = request.user
        logger = logging.getLogger(__name__)
        logger.debug("View: start search")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        search_word = body['searchTerm']
        # checkbox data comes in json form ex: 'newspapers': [{'enabled': True, 'name': 'De Standaard', 'id': 0},
        # {'$$hashKey': 'object:18', 'enabled': False, 'name': 'De Morgen', 'id': 1}
        newspapers = body['newspapers']
        format = "%d/%m/%Y"
        start_date = dateutil.parser.parse(body['startDate']).strftime(format)
        end_date = dateutil.parser.parse(body['endDate']).strftime(format)
        # iterate over checkbox values
        for newspaper in newspapers:
            if newspaper['name'] == 'De Standaard':
                standaard = newspaper['enabled']
            elif newspaper['name'] == 'De Morgen':
                morgen = newspaper['enabled']
            elif newspaper['name'] == 'HLN':
                hln = newspaper['enabled']

        if standaard:
            # start standaard archive scrape
            status = standaard_archive_scrape.delay(search_word=search_word, start_date=start_date, end_date=end_date,
                                                    email=user.email)
            continue_loop = True
            while continue_loop:
                try:
                    djcelery_task = TaskState.objects.get(task_id=status.task_id)
                    continue_loop = False
                except TaskState.DoesNotExist:
                    pass
            scrape_task = ScrapeTask(user=user, task=djcelery_task)
            scrape_task.save()
        if hln:
            # start hln archive scrape
            status = hln_archive_scrape.delay(search_word=search_word, start_date=start_date, end_date=end_date,
                                              email=user.email)
            continue_loop = True
            while continue_loop:
                try:
                    djcelery_task = TaskState.objects.get(task_id=status.task_id)
                    continue_loop = False
                except TaskState.DoesNotExist:
                    pass
            scrape_task = ScrapeTask(user=user, task=djcelery_task)
            scrape_task.save()

        return HttpResponse(json.dumps({'started': 'true'}), content_type='application/json')


def get_task_data(request):
    """
    Download data from a certain task
    http://www.azavea.com/blogs/labs/2014/03/exporting-django-querysets-to-csv/
    https://github.com/johnsensible/django-sendfile
    (access on 01/02/2016)
    :param request:
    :return
    """
    if request.method == 'POST':
        logger = logging.getLogger(__name__)
        task_id = request.POST.get('id', None)

        try:
            task = ScrapeTask.objects.get(task__task_id=task_id)
            return sendfile(request, task.data_path, attachment=True, attachment_filename='data.zip')
        except ScrapeTask.DoesNotExist:
            logger.debug("Task not found in get_task_data in newsscarper view")
            return HttpResponseRedirect('/newsscraper')