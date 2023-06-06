import jwt
from django.http import JsonResponse
from django.conf import settings
from user.models import Userprofile


def login_check(func):
    def warp(request, *args, **kwargs):
        # 获取token request.META.get('HTTP_AUTHORIZATION')
        token_jwt = request.META.get('HTTP_AUTHORIZATION')
        if token_jwt is None:
            result = {'code': 403, 'error': 'Please login!1'}
            return JsonResponse(result)
        # 校验 token
        try:
            sjwt = jwt.decode(token_jwt, settings.JWT_TOKEN_KEY, algorithms='HS256')
        except Exception as e:
            # 失败 code:403 error: Please login!
            result = {'code': 403, 'error': 'Please login!2'}
            return JsonResponse(result)
        # 获取登陆用户
        username = sjwt['username']
        user = Userprofile.objects.get(username=username)
        request.myuser = user
        return func(request, *args, **kwargs)
    return warp


def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
    except Exception as e:
        return None
    username = res['username']
    return username