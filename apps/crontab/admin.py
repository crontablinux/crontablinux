from django.contrib import admin
from apps.crontab import models

# Register your models here.
admin.site.register(models.Crontab)