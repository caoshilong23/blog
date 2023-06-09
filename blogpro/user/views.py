import json
import hashlib
import random

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache
from tools.login_dec import login_check
from tools.sms import YunTongXin
from .models import Userprofile
from .tasks import send_c


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
        sms_num = json_obj.get('sms_num')
        # 密码是否一致
        if password_1 != password_2:
            result = {'code': 10100, 'error': 'the password is not same~'}
            return JsonResponse(result)
        # 校验验证码是否正确
        old_code = cache.get('sms_%s'%(phone))
        if not old_code:
            result={'code':10108,'error':'the code is wrong'}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {'code': 10108, 'error': 'the code is wrong'}
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
        result = {'code': 10104, 'error': 'please use post'}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj.get('phone')
    # 生成随机码
    code = random.randint(1000, 9999)
    # 保存随机码 django_redis
    cache_key='sms_%s'%(phone)
    cache.set(cache_key,code,180)
    # 防止恶意发送
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code': 10110,'error':'the code is existed!'}
        return JsonResponse(result)
    # 发送随机码 -> 短信
    # send(phone,code)
    # celery版发送短信
    print('sending')
    send_c.delay(phone,code)
    print('sended')
    result = {'code': 200}
    return JsonResponse(result)


def send(phone, code):
    config = {
        'accountSid': '2c94811c87fb7ec6018819833efe0a10',
        'accountToken': '8970c932f9c446cf9fc90c5524d036b9',
        'appId': '2c94811c87fb7ec601881983403a0a17',
        'templateId': '1'
    }
    yun = YunTongXin(**config)
    res = yun.run(phone, code)