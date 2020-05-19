#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/18 18:10
# @Author  : taojianwen
# @File    : api_urls.py

from django.urls import path, include
from article.api import apis
from rest_framework import routers
from rest_framework.authtoken import views

#app_name = 'article'

route = routers.DefaultRouter()
route.register(r'articleinfo', apis.ArticleViewSet)

urlpatterns = [
    path('', include(route.urls)),
    path('auth/', views.obtain_auth_token)
]
