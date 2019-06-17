from django.contrib import admin

# Register your models here.
from apps.asset import models
from django.contrib import admin


class AssetUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(models.Asset)
admin.site.register(models.AssetUser, AssetUserAdmin)