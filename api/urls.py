from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    url(r'^posts$', views.public_posts, name='public posts'),
    url(r'^author/posts$', views.posts, name='posts'),
    url(r'^author/(?P<author_id>[\w-]+)$', views.author, name='author'),
    url(r'^author/(?P<author_id>[\w-]+)/posts$', views.author_posts, name='author posts'),
    url(r'^posts/(?P<post_id>[\w-]+)$', views.post, name='post'),
    url(r'^posts/(?P<post_id>[\w-]+)/comment$', views.comment, name='comment'),
    url(r'^friends$', views.friends, name='friends'),
    url(r'^friends/(?P<author_id>[\w-]+)$', views.friend, name='friend'),

    #These two must occur in this order to resolve correctly
    url(r'^friends/(?P<author_id>[\w-]+)/friends$', views.friends_with, name='following'),
    url(r'^friends/(?P<author_id1>[\w-]+)/(?P<author_id2>[\w-]+)$', views.is_following, name='is following'),
    url(r'^friendrequest$', views.friendrequest, name='friendrequest')
)
