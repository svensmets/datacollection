from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from newsscraper.forms import NewssiteArchiveSearchForm
import logging


class NewsScraperView(TemplateView):

    template_name = 'newsscraper/newsscraper.html'

    def dispatch(self, request, *args, **kwargs):
        return super(NewsScraperView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsScraperView, self).get_context_data(**kwargs)
        context.update(form_archive_search=NewssiteArchiveSearchForm(form_name='search_archive_form'))
        return context


def start_search(request):
    if request.method == 'post':
        logger = logging.getLogger(__name__)
        logger.debug("View: start search")