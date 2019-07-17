from django.contrib import admin
from apps.crontab import models


class CrontabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'job', 'minute', 'hour', 'day_of_month', 'month_of_year', 'day_of_week')


class CrontabAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_id', 'crontab_id', 'status')


# Register your models here.
admin.site.register(models.Crontab, CrontabAdmin)
admin.site.register(models.CrontabAsset, CrontabAssetAdmin)