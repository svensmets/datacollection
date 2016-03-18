from django.conf.urls import url
from newsscraper.views import NewsScraperView, start_archive_search


urlpatterns = [

    url(r'^start_archive_search/?$', start_archive_search, name='start_archive_search'),
    url(r'^$', NewsScraperView.as_view(), name='newsscraperview'),
]
