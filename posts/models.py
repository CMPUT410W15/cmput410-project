"""Models for the posts application."""
from django.db import models
from author.models import Author, gen_uuid


PRIVATE = 0
FRIEND = 1
FRIENDS = 2
FOAF = 3
PUBLIC = 4
SERVERONLY = 5
VISIBILITY = ((PRIVATE, 'Private'),
              (FRIEND, 'Friend'),
              (FRIENDS, 'Friends'),
              (FOAF, 'FriendOfAFriend'),
              (PUBLIC, 'Public'),
              (SERVERONLY, 'ServerOnly'))

PLAINTEXT = 0
MARKDOWN = 1
CONTENT_TYPE = ((PLAINTEXT, 'PlainText'),
                (MARKDOWN, 'Markdown'))


# Create your models here.
class Image(models.Model):
    uid = models.CharField(max_length=36, unique=True, default=gen_uuid)
    image = models.CharField(max_length=1) #TODO Proper images


class Post(models.Model):
    uid = models.CharField(max_length=36, unique=True, default=gen_uuid)
    title = models.CharField(max_length=36)
    content = models.CharField(max_length=500)
    content_type = models.IntegerField(choices=CONTENT_TYPE,
                                       default=PLAINTEXT)
    visibility = models.IntegerField(choices=VISIBILITY)
    published = models.DateTimeField(auto_now_add=True)

    send_author = models.ForeignKey(Author, related_name='sending_authors')
    receive_author = models.ForeignKey(Author, null=True,
                                       related_name='receiving_authors')
    image = models.ForeignKey(Image, null=True)

    def add_comment(self, author, comment):
        return Comment.objects.create(
            author=author,
            post=self,
            content=comment)

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
