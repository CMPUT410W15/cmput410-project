"""Models for the author application."""
import uuid

from django.db import models
from django.contrib.auth.models import User


def gen_uuid():
    return str(uuid.uuid1().hex)


# Create your models here.
class Author(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    vetted = models.BooleanField(default=False)
    host = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=100 , blank=True)
    github = models.CharField(max_length=100, blank=True)

    user = models.OneToOneField(User)
    connection = models.ManyToManyField("self", through='Connection',
                                        symmetrical=False,
                                        related_name='connected_to')

    def __unicode__(self):
        return '%s (%s)' % (self.user, self.uid)

    def befriend(self, author):
        return Connection.objects.create(
            from_author=self,
            to_author=author,
            follows=True,
            friendship_requested=True)

    def follow(self, author):
        return Connection.objects.create(
            from_author=self,
            to_author=author,
            follows=True,
            friendship_requested=False)

    def unfollow(self, author):
        Connection.objects.filter(
            from_author=self,
            to_author=author).delete()

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


class Connection(models.Model):
    from_author = models.ForeignKey(Author, related_name="from_authors")
    to_author = models.ForeignKey(Author, related_name="to_authors")
    follows = models.BooleanField(default=True)
    friendship_requested = models.BooleanField(default=True)

    def __unicode__(self):
        return 'From (%s) to (%s)' % (self.from_author, self.to_author)
