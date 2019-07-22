from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class History(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    omdb_id = models.CharField(max_length=9)
    title = models.CharField(max_length=40)
    year = models.CharField(max_length=20)
    rate = models.CharField(max_length=10)
    plot = models.CharField(max_length=600)
    datetime = models.DateTimeField()
