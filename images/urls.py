from django.conf.urls import patterns, include, url
from django.shortcuts import render
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
import views

# Create your views here.
urlpatterns = patterns('images.views',
    url(r'^$', views.images, name='images'),
    url(r'^(?P<uid>\d+)/$', views.get_image),

)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
