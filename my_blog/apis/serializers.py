#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/24 13:52
# @Author  : taojianwen
# @File    : serializers.py

from rest_framework import serializers
from article.models import ArticlePost
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    column = serializers.CharField(source='column.title')
    tags = TagListSerializerField()
    class Meta:
        model = ArticlePost
        fields = ['id', 'author', 'title', 'body', 'column', 'created', 'updated', 'total_views', 'tags']

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ret = ArticlePost.objects.create(
            author=validated_data["author"],
            body=validated_data["body"],
            title=validated_data["title"],
            column_id=validated_data["column"]["title"],
        )
        ret.tags.add(*tags)
        return ret












