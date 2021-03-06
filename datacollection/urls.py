"""datacollection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from overview.views import OverviewPage
from user_profile.views import LoginPage, LogoutPage

urlpatterns = [
    url(r'^$', OverviewPage.as_view(), name='overview'),
    url(r'^overview/$', OverviewPage.as_view(), name='overview page'),
    url(r'^login/$', LoginPage.as_view(), name='login'),
    url(r'^logout/$', LogoutPage.as_view(), name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^twitter/', include('twitter.urls')),
]
