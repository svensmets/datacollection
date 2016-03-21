from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from newsscraper.forms import NewssiteArchiveSearchForm
import logging
from newsscraper.models import ScrapeTask
from newsscraper.tasks import standaard_archive_scrape


class NewsScraperView(TemplateView):

    template_name = 'newsscraper/newsscraper.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewsScraperView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsScraperView, self).get_context_data(**kwargs)
        context.update(form_archive_search=NewssiteArchiveSearchForm(form_name='search_archive_form'))
        return context


def start_archive_search(request):
    if request.method == 'POST':
        user = request.user
        logger = logging.getLogger(__name__)
        logger.debug("View: start search")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        search_term = body['searchTerm']
        # checkbox data comes in json form ex: 'newspapers': [{'enabled': True, 'name': 'De Standaard', 'id': 0},
        # {'$$hashKey': 'object:18', 'enabled': False, 'name': 'De Morgen', 'id': 1}
        newspapers = body['newspapers']
        start_date = body['startDate']
        end_date = body['endDate']
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
            status = standaard_archive_scrape.delay(start_date=start_date, end_date=end_date)
            scrape_task = ScrapeTask(user=user, task=status.task_id)
            scrape_task.save()
        return HttpResponse(json.dumps({'started': 'true'}), content_type='application/json')
