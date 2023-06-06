from .login_dec import get_user_by_request
from django.core.cache import cache

def cache_set(expire):
    def _cache_set(func):
        def wrapper(request,*args,**kwargs):
            # 缓存列表页 区分场景
            if 't_id' in request.GET:
                return func(request,*args,**kwargs)
            # 生成出 正确的cache_key 【】
            visitor_user = get_user_by_request(request)
            visitor_username = None
            if visitor_user:
                visitor_username = visitor_user
            author_username = kwargs['author_id']
            # 根据不同的访问者给出不同的cache_key
            full_path = request.get_full_path()
            if visitor_username == author_username:
                cache_key = 'topics_cache_self_%s'%full_path
            else:
                cache_key = 'topics_cache_%s'%full_path

            # 判断是否有缓存
            res = cache.get(cache_key)
            if res:
                print('---cache in')
                return res
            # 执行视图
            res = func(request,*args,**kwargs)
            # 保存缓存
            cache.set(cache_key,res,expire)
            # 返回响应
            return res
        return wrapper
    return _cache_set
