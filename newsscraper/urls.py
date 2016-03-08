from django.conf.urls import url
from newsscraper.views import NewsScraperView
urlpatterns = [
    url(r'^$', NewsScraperView.as_view(), name='newsscraperview'),
]
