from django.db import models
from django.conf import settings
from django.utils import timezone

from .model.urldb import UrlDB
from .model.urlmanager import User, UrlFile


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(
            default=timezone.now)
    published_at = models.DateTimeField(
            blank=True, null=True)


    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title


