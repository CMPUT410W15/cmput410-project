from django.shortcuts import render
import views

# Create your views here.
urlpatterns = patterns('',
    url(r'^images/$', views.images, name='images'),
)
