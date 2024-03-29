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
from apps.asset.views import AssetListView, AssetView, AssetUserView, AssetUserListView, AssetCrons, AssetCron


urlpatterns = [
    path('', AssetListView.as_view()),
    path('/<int:asset_id>', AssetView.as_view()),
    path('/<int:asset_id>/cron', AssetCrons.as_view()),
    path('/<int:asset_id>/cron/<int:cron_id>', AssetCron.as_view()),

    path('/users', AssetUserListView.as_view()),
    path('/users/<int:user_id>', AssetUserView.as_view()),
]
