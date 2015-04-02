from django.db import models
from common.util import gen_uuid
import uuid
import os

PRIVATE = 0
FRIEND = 1
FRIENDS = 2
FOAF = 3
PUBLIC = 4
SERVERONLY = 5
VISIBILITY = ((PRIVATE, 'Private'),
              (FRIENDS, 'Friends'),
              (FOAF, 'FriendOfAFriend'),
              (PUBLIC, 'Public'),
              (SERVERONLY, 'ServerOnly'))

# Create your models here.
class Image(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    image = models.ImageField(upload_to = 'upload/', default = 'upload/None/no-img.jpg')
    visibility = models.IntegerField(choices=VISIBILITY)
    def __unicode__(self):
        return '%s' % self.uid

    @models.permalink
    def get_absolute_url(self):
        return 'url', (), {'uid': self.uid}

