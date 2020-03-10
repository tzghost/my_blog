#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/20 9:13
# @Author  : taojianwen
# @File    : forms.py
# 引入表单类
from django import forms
# 引入文章模型
from .models import ArticlePost

# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'tags', 'avatar', 'column')
        widgets = {
            'body': forms.Textarea(attrs={
                'class': "form-control",
                'rows': '12',
            }),
            'column': forms.Select(attrs={
                'class': "form-control col-3",
            }),
            'title': forms.TextInput(attrs={
                'class': "form-control",
                'rows': '12',
            }),
            'tags': forms.TextInput(attrs={
                'class': "form-control col-12",
            }),
        }
