from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.item)
admin.site.register(models.bid)
admin.site.register(models.comment)
admin.site.register(models.watchlist)