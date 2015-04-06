"""Models for the posts application."""
import CommonMark
from django.db import models
from author.models import Author
from images.models import Image
from django.utils.safestring import mark_safe
from common.util import gen_uuid

from management.models import Node

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
class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.category


class Post(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    title = models.CharField(max_length=36)
    description = models.CharField(max_length=200, blank=True)
    content = models.CharField(max_length=500)
    content_type = models.IntegerField(choices=CONTENT_TYPE,
                                       default=PLAINTEXT)
    visibility = models.IntegerField(choices=VISIBILITY)
    published = models.DateTimeField(auto_now_add=True)

    send_author = models.ForeignKey(Author, related_name='posts_sent')
    # receive_author is no longer supported
    receive_author = models.ForeignKey(Author, null=True, blank=True,
                                       related_name='posts_received')
    image = models.ForeignKey(Image, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

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
            "description": self.description,
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
        #Return comments sorted from newest to oldest
        comments= Comment.objects.filter(post=self)
        comments = sorted(comments, key=lambda x: x.published, reverse=True)
        return comments

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

        if self.send_author == author:
            return True

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

    def markdown_to_html(self):
        #If the content is markdown, convert it
        #Else just return the plaintext content
        if (self.content_type == 0):
            return self.content
        else:
            parser = CommonMark.DocParser()
            renderer = CommonMark.HTMLRenderer()
            ast = parser.parse(self.content)
            html = renderer.render(ast)
            return mark_safe(html)

    def get_post_host(self):
        #Get the host of a post (their node name, not their node url)
        url=self.send_author.host
        if url in 'http://thought-bubble.herokuapp.com/main/api/':
            return 'thoughtbubble'
        else:
            return 'hindlebook'

    def has_image(self):
        if self.image==None:
            return False
        else:
            return True

    def get_image(self):
        image_location=self.image.image
        return image_location
        
class Comment(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    content = models.CharField(max_length=200)
    published = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(Author)
    post = models.ForeignKey(Post)

    def __unicode__(self):
        #return 'Author: %s Post: %s' % (self.author, self.post)
        return '%s: %s' %(self.author,self.content)

    #To display only the username or display name with comment, not uid as well
    def get_comment_body(self):
        return '%s: %s' %(self.author.get_name(),self.content)

    def to_dict(self):
        return {
            "author": self.author.to_dict(),
            "comment": self.content,
            "pubDate": str(self.published),
            "guid": self.uid,
        }
