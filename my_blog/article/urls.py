#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:36
# @Author  : taojianwen
# @File    : urls.py.py

from django.urls import path
from . import views

app_name = 'article'

urlpatterns = [
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),
    path('increase-links/<int:pk>/', views.IncreaseLinkesView.as_view(), name='increase_likes'),

    #视图类
    path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail_view'),
    path('list-view/', views.ArticleListView.as_view(), name='list_view'),
    path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
    path('delete-view/<int:pk>', views.ArticleDeleteView.as_view(), name='delete_view'),
    #path('update-view/<int:pk>', views.AriticleUpdateView.as_view(), name='update-view'),
]
