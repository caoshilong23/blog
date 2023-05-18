import json
import hashlib
import random

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse

from tools.login_dec import login_check
from .models import Userprofile

# django提供了一个装饰器method_decorator
# Create your views here.
# 异常码10100-10199

class UserViews(View):
    def get(self, request, username=None):
        if username:
            # v1/user/username
            print(username)
            try:
                user = Userprofile.objects.get(username=username)
            except Exception as e:
                result = {'code': 10102, 'error': 'the username is error'}
                return JsonResponse(result)
            result = {'code': 200, 'username': username, 'data': {
                'info': user.info,
                'sign': user.sign,
                'nickname': user.nickname,
                'avatar': str(user.avatar)
            }}
            return JsonResponse(result)

        else:
            # v1/user
            pass

    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        phone = json_obj.get('phone')
        # 密码是否一致
        if password_1 != password_2:
            result = {'code': 10100, 'error': 'the password is not same~'}
            return JsonResponse(result)
        # 用户名是否存在
        old_users = Userprofile.objects.filter(username=username)
        if old_users:
            result = {'code': 10101, 'error': 'the username is existed~'}
            return JsonResponse(result)
        # Userprofile插入数据
        p_m = hashlib.md5()
        p_m.update(password_1.encode())
        Userprofile.objects.create(username=username, nickname=username, password=p_m.hexdigest(), email=email,
                                   phone=phone)
        result = {'code': 200, 'username': username, 'data': {}}
        return JsonResponse(result)

    @method_decorator(login_check)
    def put(self, request, username=None):
        json_str = request.body
        json_obj = json.loads(json_str)
        user = request.myuser
        user.info = json_obj['info']
        user.sign = json_obj['sign']
        user.nickname = json_obj['nickname']
        user.save()
        return JsonResponse({'code': 200})

@login_check
def users_views(request, username):
    if request.method != 'POST':
        result = {'code': 10103, 'error': 'please use POST!'}
        return JsonResponse(result)
    user = request.myuser
    avatar = request.FILES['avatar']
    user.avatar = avatar
    user.save()
    return JsonResponse({'code': 200})


def send_sms(request):
    if request.method != 'POST':
        result={'code':10104,'error':'please use post'}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj.get('phone')

    # 生成随机码
    code = random.randint(1000,9999)
    # 保存随机码 django_redis

    # 发送随机码 -> 短信

    result={'code':200}
    return JsonResponse(result)
