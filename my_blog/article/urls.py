#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:36
# @Author  : taojianwen
# @File    : urls.py.py

from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'article'

route = routers.DefaultRouter()
route.register('articleinfo', views.ArticleViewSet)

urlpatterns = [
    path('increase-links/<int:pk>/', views.IncreaseLinkesView.as_view(), name='increase_likes'),
    path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail_view'),
    path('list-view/', views.ArticleListView.as_view(), name='list_view'),
    path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
    path('delete-view/<int:pk>', views.ArticleDeleteView.as_view(), name='delete_view'),
    path('update-view/<int:pk>', views.ArticleUpdateView.as_view(), name='update-view'),
    path('api/', include(route.urls)),
]
