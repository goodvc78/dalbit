from django.contrib import admin
from .models import Post
from .model.urldb import UrlDB
from .model.urlmanager import User, UrlFile, CheckPoint

admin.site.register(Post)
admin.site.register(UrlDB)
admin.site.register(User)
admin.site.register(UrlFile)
admin.site.register(CheckPoint)
