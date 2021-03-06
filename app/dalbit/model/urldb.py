from django.db import models
from django.conf import settings
from django.utils import timezone


class UrlDB(models.Model):
    gtype = models.CharField(max_length=2)
    gid = models.CharField(max_length=10)
    pid = models.CharField(max_length=10)
    cate_desc = models.CharField(max_length=10)
    dtype = models.IntegerField(default=1) # 1=url, 2=ip
    host = models.CharField(max_length=256)
    path = models.CharField(max_length=256, default="/")
    description = models.CharField(max_length=256, default="none")
    reg_date = models.DateTimeField(
            default=timezone.now)
    mod_date = models.DateTimeField(
            blank=True, null=True)

    def __str__(self):
        return '{}-{}-{}:{} {}'.format(self.gid, self.pid, self.cate_desc, self.host, self.path)
    
class Category(models.Model):
    gtype = models.CharField(max_length=2)
    gid = models.CharField(max_length=10)
    gname = models.CharField(max_length=50)
    pid = models.CharField(max_length=10)
    # seq = models.IntegerField(null=True)
    dtype = models.IntegerField(default=1) # 1=url, 2=ip
    data = models.CharField(max_length=256, null=True)

    def __str__(self):
        return '{}-{} : {}'.format(self.gid, self.gname, self.data[:50])

class Migration_UrlDB(models.Model):
    gtype = models.CharField(max_length=2)
    gid = models.CharField(max_length=10)
    pid = models.CharField(max_length=10)
    cate_desc = models.CharField(max_length=10)
    dtype = models.IntegerField(default=1) # 1=url, 2=ip
    host = models.CharField(max_length=256)
    path = models.CharField(max_length=256, default="/")
    description = models.CharField(max_length=256, default="/")
    reg_date = models.DateTimeField(
            default=timezone.now)
    mod_date = models.DateTimeField(
            blank=True, null=True)

    def __str__(self):
        return '{}-{}-{}:{} {}'.format(self.gid, self.pid, self.cate_desc, self.host, self.path)


