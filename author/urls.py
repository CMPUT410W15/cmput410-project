from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    url(r'^$', views.friends, name='friends'),
    url(r'^befriend/(?P<uid>[^/]+)/$', views.befriend, name='befriend'),
    url(r'^unbefriend/(?P<uid>[^/]+)/$', views.unbefriend, name='unbefriend'),
    url(r'^follow/(?P<uid>[^/]+)/$', views.follow, name='follow'),
    url(r'^unfollow/(?P<uid>[^/]+)/$', views.unfollow, name='unfollow'),
    url(r'^edit/$', views.edit, name='edit'),
)
