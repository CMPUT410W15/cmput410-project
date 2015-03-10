from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from posts import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bookmarks.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.post, name='post'),
    url(r'^delete/(?P<uid>\w+)$', views.delete_post, name='delete_post')
)
