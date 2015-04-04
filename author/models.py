"""Models for the author application."""
from django.db import models
from django.contrib.auth.models import User
from images.models import Image
from common.util import gen_uuid


class FollowYourselfError(Exception): pass


# Create your models here.
class Author(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    host = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=100 , blank=True)
    github = models.CharField(max_length=100, blank=True)

    displayname = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, null=True)
    picture = models.ForeignKey(Image, null=True, blank=True)
    connection = models.ManyToManyField("self", through='Connection',
                                        symmetrical=False,
                                        related_name='connected_to')

    def __unicode__(self):
        uname = self.user.username if self.user else self.displayname
        return '%s (%s)' % (uname, self.uid)

    def to_dict(self):
        name = self.user.username if self.user else self.displayname
        return {
            "id": self.uid,
            "host": self.host,
            "displayname": name,
            "url": "http://cs410.cs.ualberta.ca:41084/api/author/ " + self.uid,
        }

    def befriend(self, author):
        if author == self:
            raise FollowYourselfError
        return Connection.objects.create(
            from_author=self,
            to_author=author,
            follows=True,
            friendship_requested=True)

    def follow(self, author):
        if author == self:
            raise FollowYourselfError
        if self not in author.get_followers():
            return Connection.objects.create(
                from_author=self,
                to_author=author,
                follows=True,
                friendship_requested=False)

    def unfollow(self, author):
        Connection.objects.filter(
            from_author=self,
            to_author=author).delete()

    def is_followee(self, author):
        return self.connection.filter(
            to_authors__follows=True,
            to_authors__from_author=self,
            to_authors__to_author=author,
            ).exists()

    def get_followees(self):
        return self.connection.filter(
            to_authors__follows=True,
            to_authors__from_author=self,
            )

    def get_followers(self):
        return self.connected_to.filter(
            from_authors__follows=True,
            from_authors__to_author=self,
            )

    def is_friend(self, author):
        return self.connection.filter(
            to_authors__follows=True,
            to_authors__from_author=self,
            to_authors__to_author=author,
            from_authors__follows=True,
            from_authors__to_author=self).exists()

    def get_friends(self):
        return self.connection.filter(
            to_authors__follows=True,
            to_authors__from_author=self,
            from_authors__follows=True,
            from_authors__to_author=self)

    def get_friend_requests(self):
        return self.connected_to.filter(
            from_authors__friendship_requested=True,
            from_authors__to_author=self,
            )

    def get_friends_of_friends(self):
        return {f: f.get_friends() for f in self.get_friends()}

    def get_posts(self, visibility=None):
        if visibility == None:
            return self.posts_sent.all()
        else:
            return self.posts_sent.filter(visibility=visibility)

    def get_received_posts(self, visibility=None):
        if visibility == None:
            return self.posts_received.all()
        else:
            return self.posts_received.filter(visibility=visibility)

    def get_comments(self):
        return self.comment_set.all()

    def get_author_hostname(self):
        #Get the host of a author (their node name, not their node url)
        url=self.host
        if url in 'http://thought-bubble.herokuapp.com/main/api/':
            return 'thoughtbubble'

        else:
            return 'hindlebook'

    def has_picture(self):
        if self.picture==None:
            return False
        else:
            return True

    def get_picture(self):
        picture_location=self.picture.image
        return picture_location



class Connection(models.Model):
    from_author = models.ForeignKey(Author, related_name="from_authors")
    to_author = models.ForeignKey(Author, related_name="to_authors")
    follows = models.BooleanField(default=True)
    friendship_requested = models.BooleanField(default=True)

    def __unicode__(self):
        return 'From (%s) to (%s)' % (self.from_author, self.to_author)
