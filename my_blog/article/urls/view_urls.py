#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/19 14:36
# @Author  : taojianwen
# @File    : view_urls.py.py

from django.urls import path, include
from article import views
app_name = 'article'

urlpatterns = [
    path('increase-links/<int:pk>/', views.IncreaseLinkesView.as_view(), name='increase_likes'),
    path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail_view'),
    path('course-detail-view/<int:pk>/', views.ArticleCourseDetailView.as_view(), name='course_detail_view'),
    path('list-view/', views.ArticleListView.as_view(), name='list_view'),
    path('course-view/', views.ArticleCourseView.as_view(), name='course_view'),
    path('archive-view/', views.ArticleArchiveView.as_view(), name='archive_view'),
    path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
    path('delete-view/<int:pk>', views.ArticleDeleteView.as_view(), name='delete_view'),
    path('update-view/<int:pk>', views.ArticleUpdateView.as_view(), name='update-view'),
]
