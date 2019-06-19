from django.contrib import admin
from apps.ops import models


class AdhocAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'hosts', 'tasks')


# Register your models here.
admin.site.register(models.Adhoc, AdhocAdmin)