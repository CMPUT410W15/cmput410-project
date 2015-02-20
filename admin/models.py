from django.db import models


class Node(models.Model):
    url = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100) #TBD

