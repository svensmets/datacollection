from django.conf.urls import url
from twitter.views import HomescreenPage, AddTwitterKeys, lookupname, profile_information_search, get_tasks, \
    tweets_by_name_search, tweets_by_searchterm_search, get_task_data, random_tweets_search
from user_profile.views import LoginPage, LogoutPage

urlpatterns = [
    url(r'^$', HomescreenPage.as_view(), name='twit'),
    url(r'^homescreen/$', HomescreenPage.as_view(), name='homescreen'),
    url(r'^twitter/$', HomescreenPage.as_view(), name='twitter'),
    url(r'^addkeys/$', AddTwitterKeys.as_view(), name='add keys'),
    url(r'^login/$', LoginPage.as_view(), name='login'),
    url(r'^logout/$', LogoutPage.as_view(), name='logout'),
    url(r'^lookupname/$', lookupname, name='lookup_name'),
    url(r'^profile-information-search/$', profile_information_search, name='profile_information'),
    url(r'^get_tasks/$', get_tasks, name='get tasks'),
    url(r'^tweets_by_name_search/$', tweets_by_name_search, name='tweets_by_name'),
    url(r'^tweets_by_searchterm_search/$', tweets_by_searchterm_search, name='tweets_by_searchterm'),
    url(r'^get_task_data/$', get_task_data,name='get_task_data'),
    url(r'^random_tweets_search/$', random_tweets_search, name='Random tweets search'),
]
