#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/21 10:12
# @Author  : taojianwen
# @File    : forms.py

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
