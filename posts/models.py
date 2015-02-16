"""Models for the posts application."""
import uuid

from django.db import models
from author.models import Author, gen_uuid


PRIVATE = 0
FRIENDS = 1
FOAF = 2
PUBLIC = 3
SERVERONLY = 4
VISIBILITY = ((PRIVATE, 'Private'),
              (FRIENDS, 'Friends'),
              (FOAF, 'FriendOfAFriend'),
              (PUBLIC, 'Public'),
              (SERVERONLY, 'ServerOnly'))


# Create your models here.
class Image(models.Model):
    uid = models.CharField(max_length=36, unique=True, default=gen_uuid)
    image = models.CharField(max_length=1) #TODO Proper images


class Post(models.Model):
    uid = models.CharField(max_length=36, unique=True, default=gen_uuid)
    title = models.CharField(max_length=36)
    content = models.CharField(max_length=500)
    visibility = models.IntegerField(choices=VISIBILITY)
    published = models.DateTimeField(auto_now_add=True)

    image = models.ForeignKey(Image, null=True)
    author = models.ForeignKey(Author)

    def add_comment(self, commentary):
        return Comment.objects.create(
            content=commentary,
            post=self)

    def remove_comment(self, uid):
        Comment.objects.filter(
            uid=uid,
            post=self).delete()

    def get_comments(self):
        return Comment.objects.filter(post=self)


class Comment(models.Model):
    uid = models.CharField(max_length=36, unique=True, default=gen_uuid)
    content = models.CharField(max_length=200)
    published = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(Author)
    post = models.ForeignKey(Post)
