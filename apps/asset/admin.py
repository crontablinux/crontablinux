from django.contrib import admin

# Register your models here.
from apps.asset import models


admin.site.register(models.Asset)
admin.site.register(models.AssetUser)