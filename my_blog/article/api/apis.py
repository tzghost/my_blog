#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/18 15:29
# @Author  : taojianwen
# @File    : apis.py

from article.models import ArticlePost
from rest_framework import viewsets, permissions
from article.api.serializers import ArticleSerializer

class IsOwerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            return True
        return obj.author == request.user

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = ArticlePost.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwerOrReadOnly)

