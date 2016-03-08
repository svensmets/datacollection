from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from newsscraper.forms import NewssiteArchiveSearchForm
import logging


class NewsScraperView(TemplateView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        search_archive_form = NewssiteArchiveSearchForm
        return render(request, 'newsscraper/newsscraper.html', {'search_archive_form': search_archive_form})


def start_search(request):
    if request.method == 'post':
        logger = logging.getLogger(__name__)
        logger.debug("View: start search")