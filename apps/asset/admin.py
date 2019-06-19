from django.contrib import admin

# Register your models here.
from apps.asset import models
from django.contrib import admin


class AssetUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ip', 'user_id')


admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.AssetUser, AssetUserAdmin)