from __future__ import unicode_literals

from django.db import models


class User(models.Model):
    username = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)

