from django.conf.urls import patterns, include, url
from django.contrib import admin
from login.views import *

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from posts.views import *
from images.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'socialdistribution.views.home', name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^friends/', include('author.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^post/', include('posts.urls')),
    url(r'^images/', include('images.urls')),

	url(r'^$', home),
    url(r'^logout/$', logout_page),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'), # If user is not login it will redirect to login page
    url(r'^register/$', register),
    url(r'^register/success/$', register_success),
    url(r'^home/$', home),
    url(r'^home/([^/]+)/$', authorhome),
    url(r'^home/author/posts/$',personal_stream),
    url(r'^home/author/posts/friends/$',personal_stream_friends),
    url(r'^post/(?P<post_id>[\w-]+)/$', comment, name="add_comment"),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
