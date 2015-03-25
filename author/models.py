"""Models for the author application."""
from django.db import models
from django.contrib.auth.models import User
from images.models import Image
from common.util import gen_uuid, get_request_to_json, get_nodes


class FollowYourselfError(Exception): pass


def reset_foreign_authors():
    #Author.objects.filter(user=None).delete()

    for node in get_nodes():
        remote_authors = []
        for author in get_request_to_json(node.url + 'authors'):
            a = {'uid': author['id'],
                 'displayname': author['displayname'],
                 'host': author['host']}
            author_obj, created = Author.objects.get_or_create(**a)
            remote_authors.append(author_obj)

        for a1 in remote_authors[:]:

            remote_authors.remove(a1)
            for a2 in remote_authors:
                friends_url = 'friends/%s/%s' % (a1.uid, a2.uid)
                result = get_request_to_json(node.url + friends_url)
                if result not in [401, 404] and result['friends'] == 'YES':
                    a1.follow(a2)
                    a2.follow(a1)

            for a2 in Author.objects.all():
                friends_url = 'friends/%s/%s' % (a1.uid, a2.uid)
                result = get_request_to_json(node.url + friends_url)
                if result not in [401, 404] and result['friends'] == 'YES':
                    a1.follow(a2)
                    a2.follow(a1)


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
        #return '%s (%s)' % (self.user, self.uid)
        return self.user.username if self.user else self.displayname

    def to_dict(self):
        name = self.user.username if self.user else self.displayname
        return {
            "id": self.uid,
            "host": self.host,
            "displayname": name,
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


class Connection(models.Model):
    from_author = models.ForeignKey(Author, related_name="from_authors")
    to_author = models.ForeignKey(Author, related_name="to_authors")
    follows = models.BooleanField(default=True)
    friendship_requested = models.BooleanField(default=True)

    def __unicode__(self):
        return 'From (%s) to (%s)' % (self.from_author, self.to_author)
