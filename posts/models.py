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
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    image = models.ImageField()
    visibility = models.IntegerField(choices=VISIBILITY, default=PUBLIC)

    def __unicode__(self):
        return '%s' % self.uid


class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.category


class Post(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    title = models.CharField(max_length=36)
    content = models.CharField(max_length=500)
    content_type = models.IntegerField(choices=CONTENT_TYPE,
                                       default=PLAINTEXT)
    visibility = models.IntegerField(choices=VISIBILITY)
    published = models.DateTimeField(auto_now_add=True)

    send_author = models.ForeignKey(Author, related_name='sending_authors')
    receive_author = models.ForeignKey(Author, null=True,
                                       related_name='receiving_authors')
    image = models.ForeignKey(Image, null=True, blank=True)
    categories = models.ManyToManyField(Category)

    def to_dict(self):
        content_types = ["text/plain", "text/x-markdown"]
        visibilities = [
            "PRIVATE",
            "PRIVATE",
            "FRIENDS",
            "FOAF",
            "PUBLIC",
            "SERVERONLY"
        ]

        return {
            "title": self.title,
            "description": "", #Missing. See #77
            "image": "", #Missing see #78
            "content-type": content_types[self.content_type],
            "content": self.content,
            "author": self.send_author.to_dict(),
            "categories": [], #Missing, see #79
            "comments": [ x.to_dict() for x in self.get_comments() ],
            "pubDate": str(self.published),
            "guid": self.uid,
            "visibility": visibilities[self.visibility],
        }


    def __unicode__(self):
        return '%s' % self.title

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

    def add_category(self, category):
        return self.categories.add(category)

    def get_categories(self):
        return self.categories.all()

    def visible_to(self, author):
        # VISIBILITY = ((PRIVATE, 'Private'),
        #               (FRIEND, 'Friend'),
        #               (FRIENDS, 'Friends'),
        #               (FOAF, 'FriendOfAFriend'),
        #               (PUBLIC, 'Public'),
        #               (SERVERONLY, 'ServerOnly'))
        if self.visibility == PUBLIC:
            return True
        elif self.visibility == FRIEND:
            return author == self.receive_author
        elif self.visibility == FRIENDS:
            return self.send_author.is_friend(author)
        elif self.visibility == FOAF:
            return True # TODO: Implement FOAF
        elif self.visibility == PRIVATE:
            return self.send_author == author
        elif self.visibility == SERVERONLY:
            return self.send_author.host == author.host

        return True

class Comment(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    content = models.CharField(max_length=200)
    published = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(Author)
    post = models.ForeignKey(Post)

    def __unicode__(self):
        return 'Author: %s Post: %s' % (self.author, self.post)

    def to_dict(self):
        return {
            "author": self.author.to_dict(),
            "comment": self.content,
            "pubDate": str(self.published),
            "guid": self.uid,
        }
