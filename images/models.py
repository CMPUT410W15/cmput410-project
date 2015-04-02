from django.db import models
from common.util import gen_uuid

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

class Image(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    image = models.ImageField(upload_to = 'upload/', default = 'upload/None/no-img.jpg')
    visibility = models.IntegerField(choices=VISIBILITY)

    def __unicode__(self):
        return '%s' % self.uid

    def get_url(self):
        return '/images/' + self.uid

    def visible_to(self, author):
        from posts.models import Post

        try:
            post = Post.objects.get(image=self)
        except Post.DoesNotExist:
            return True

        return post.visible_to(author)
