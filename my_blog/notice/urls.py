#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/22 9:43
# @Author  : taojianwen
# @File    : view_urls.py

from django.urls import path
from . import views

app_name = 'notice'

urlpatterns = [
    path('list/', views.CommentNoticeListView.as_view(), name='list'),
    path('update/', views.CommentNoticeUpdateView.as_view(), name='update'),

]
