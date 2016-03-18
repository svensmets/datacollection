from django.contrib.auth.decorators import login_required
import json
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from newsscraper.forms import NewssiteArchiveSearchForm
import logging


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
