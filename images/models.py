from django.db import models
from common.util import gen_uuid

# Create your models here.
class Image(models.Model):
    uid = models.CharField(max_length=36, unique=True,
                           editable=False, default=gen_uuid)
    image = models.ImageField()

    def __unicode__(self):
        return '%s' % self.uid
        