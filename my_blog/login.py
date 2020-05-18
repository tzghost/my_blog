#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/18 14:40
# @Author  : taojianwen
# @File    : login.py

from django.http import JsonResponse
from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib import auth


@api_view(['POST'])
def login(request):
    receive = request.data
    username = receive.get('username')
    password = receive.get('password')
    user = auth.authenticate(username=username, password=password)
    if not user:
        return HttpResponse("用户名和密码不匹配")
    # 校验通过
    # 删除原有的Token
    old_token = Token.objects.filter(user=user)
    old_token.delete()
    # 创建新的Token
    token = Token.objects.create(user=user)
    return JsonResponse({"username": user.username, "token": token.key})

@api_view(['POST'])
def do_something(request):
    receive = request.data
    print(receive)
    if request.user.is_authenticated:   # 验证Token是否正确
        print("Do something...")
        return JsonResponse({"msg": "验证通过"})
    else:
        print("验证失败")
        return JsonResponse({"msg": "验证失败"})
