"""CrontabLinux URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from apps.crontab.views import CronListView, CronView, CronAssetListView, CronAssetView


urlpatterns = [
    path('', CronListView.as_view()),
    path('/<int:cron_id>', CronView.as_view()),

    path('/assets', CronAssetListView.as_view()),
    path('/assets/<int:cron_asset_id>', CronAssetView.as_view()),

]
