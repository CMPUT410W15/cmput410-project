from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'socialdistribution.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.friends, name='friends'),
    url(r'^befriend/(?P<user>\w+)/$', views.befriend, name='befriend'),
    url(r'^unbefriend/(?P<user>\w+)/$', views.unbefriend, name='unbefriend'),
    url(r'^follow/(?P<user>\w+)/$', views.follow, name='follow'),
    url(r'^unfollow/(?P<user>\w+)/$', views.unfollow, name='unfollow'),
)
