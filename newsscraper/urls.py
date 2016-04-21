from django.conf.urls import url
from newsscraper.views import NewsScraperView, start_archive_search, task_list, get_task_data

urlpatterns = [

    url(r'^start_archive_search/?$', start_archive_search, name='start_archive_search'),
    url(r'^$', NewsScraperView.as_view(), name='newsscraperview'),
    url(r'^tasks/?$', task_list, name='task_list'),
    url(r'^get_task_data/$', get_task_data,name='get_task_data'),
]
