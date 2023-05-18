import json
import hashlib
import time

import jwt
from django.shortcuts import render
from django.http import JsonResponse
from user.models import Userprofile
from django.conf import settings


# Create your views here.
# 异常码10200-10299

def tokens(request):
    if request.method != 'POST':
        result = {'code': 10200, 'error': 'Please use POST!'}
        return JsonResponse(result)

    elif request.method == 'POST':
        json_str = request.body
        json_body = json.loads(json_str)
        username = json_body['username']
        # 检测用户名是否存在
        try:
            user = Userprofile.objects.get(username=username)
        except:
            result = {'code': 10201, 'error': 'the username is not existed~'}
            return JsonResponse(result)
        # 密码加密
        password = json_body['password']
        p_m = hashlib.md5()
        p_m.update(password.encode())

        # 检测密码是否
        if user.password == p_m.hexdigest():
            # 记录会话状态
            token = make_token(username)
            result = {'code': 200, 'username': username, 'data': {'token': token}}
        elif user.password != p_m.hexdigest():
            result = {'code': 10202, 'error': 'the username or password is error~'}
        return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'username': username, 'exp': now_t + expire}
    return jwt.encode(payload_data, key, algorithm='HS256')
