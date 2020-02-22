#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:36
# @Author  : taojianwen
# @File    : urls.py.py

from django.urls import path
from . import views

app_name = 'article'

urlpatterns = [
    path('article-list/', views.article_list, name='article-list'),
    #文章详情
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    #写文章
    path('article-create/', views.article_create, name='article_create'),
    # 删除文章
    path('article-delete/<int:id>/', views.article_delete, name='article_delete'),
    # 安全删除文章
    path('article-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),
    path('increase-links/<int:id>/', views.IncreaseLinkesView.as_view(), name='increase_likes'),
]
