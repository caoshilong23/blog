import json

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache
from tools.login_dec import login_check, get_user_by_request
from tools.cache_dec import cache_set
from django.utils.decorators import method_decorator
from .models import Topic
from user.models import Userprofile
from message.models import Message


# Create your views here.
# 异常码10300-10399
class TopicViews(View):

    def clear_cache(self, request):
        path = request.path_info
        cache_key_p = ['topics_cache_self_', 'topics_cache_']
        cache_key_h = ['', '?category=tec', '?category=no-tec']
        all_cache = []
        for key_p in cache_key_p:
            for key_h in cache_key_h:
                all_cache.append(key_p + path + key_h)
        cache.delete_many(all_cache)

    def make_topic_res(self, author, author_topic, is_self):
        if is_self:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()
        next_id = next_topic.id if next_topic else None
        next_title = next_topic.title if next_topic else ''
        last_id = last_topic.id if last_topic else None
        last_title = last_topic if last_topic else ''

        # 关联留言和回复
        all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list = []
        rep_dic = {}
        m_count = 0
        for msg in all_messages:
            if msg.parent_message:
                # 回复
                rep_dic.setdefault(msg.parent_message, [])
                rep_dic[msg.parent_message].append({'msg_id': msg.id, 'publisher': msg.publisher.nickname,
                                                    'publisher_avatar': str(msg.publisher.avatar),
                                                    'centent': msg.content,
                                                    'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                # 留言
                m_count += 1
                msg_list.append({'id': msg.id, 'content': msg.content, 'publisher': msg.publisher.nickname,
                                 'publisher_avatar': str(msg.publisher.avatar),
                                 'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'reply': []})
        for m in msg_list:
            if m['id'] in rep_dic:
                m['reply'] = rep_dic[m['id']]

        res = {'code': 200, 'data': {}}
        res['data']['nickname'] = author.nickname
        res['data']['title'] = author_topic.title
        res['data']['category'] = author_topic.category
        res['data']['created_time'] = author_topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        res['data']['content'] = author_topic.content
        res['data']['introduce'] = author_topic.introduce
        res['data']['author'] = author.nickname
        res['data']['last_id'] = last_id
        res['data']['last_title'] = last_title
        res['data']['next_id'] = next_id
        res['data']['next_title'] = next_title
        res['data']['messages'] = msg_list
        res['data']['messages_count'] = m_count
        return res

    def make_topics_res(self, author, author_topics):
        res = {'code': 200, 'data': {}}
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['created_time'] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
            d['introduce'] = topic.introduce
            d['author'] = author.nickname
            topics_res.append(d)
        res['data']['nickname'] = author.nickname
        res['data']['topics'] = topics_res
        return res

    @method_decorator(login_check)
    def post(self, request, author_id):
        author = request.myuser
        # {"content": "<p><span style=\"font-weight: bold;\">222</span><br></p>", "content_text": "222",
        #  "limit": "public", "title": "111", "category": "tec"}
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        content = json_obj.get('content')
        content_text = json_obj.get('content_text')[:30]
        limit = json_obj.get('limit')
        category = json_obj.get('category')
        if limit not in ['public', 'private']:
            return JsonResponse({'code': 10300, 'error': 'the limit error~'})
        if category not in ['tec', 'no-tec']:
            return JsonResponse({'code': 10301, 'error': 'the category error~'})
        Topic.objects.create(content=content, introduce=content_text, limit=limit, category=category, author=author,
                             title=title)
        self.clear_cache(request)
        return JsonResponse({'code': 200})

    @method_decorator(cache_set(300))
    def get(self, request, author_id):
        try:
            author = Userprofile.objects.get(username=author_id)
        except Exception as e:
            result = {'code': 10302, 'error': 'the username is error~'}
            return JsonResponse(result)
        # 判断访问者与作者
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor
        t_id = request.GET.get('t_id')
        if t_id:
            # 获取单篇文章的详情
            t_id = int(t_id)
            is_self = False
            if visitor_name == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(author=author_id, id=t_id)
                    res = self.make_topic_res(author, author_topic, is_self)
                    return JsonResponse(res)
                except Exception as e:
                    res = {'code': 10303, 'error': 'the topic is not exist1'}
                    return JsonResponse(res)
            else:
                try:
                    author_topic = Topic.objects.get(author=author_id, limit='public', id=t_id)
                    res = self.make_topic_res(author, author_topic, is_self)
                    return JsonResponse(res)
                except Exception as e:
                    res = {'code': 10304, 'error': 'the topic is not exist2'}
                    return JsonResponse(res)

        else:
            print('---views in')
            # 获取某作者的全部文章
            category = request.GET.get('category')
            if category:
                if visitor_name == author_id:
                    author_topics = Topic.objects.filter(author=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author=author_id, limit='public', category=category)
            else:
                if visitor_name == author_id:
                    author_topics = Topic.objects.filter(author=author_id)
                else:
                    author_topics = Topic.objects.filter(author=author_id, limit='public')
            result = self.make_topics_res(author, author_topics)
            return JsonResponse(result)

    @method_decorator(login_check)
    def delete(self, request, author_id):  # 还需要调试
        delete_name = request.myuser.nickname
        t_id = int(request.GET.get('t_id'))
        if t_id and delete_name == author_id:
            Topic.objects.get(id=t_id).delete()
            self.clear_cache(request)
            return JsonResponse({'code': 200})
        else:
            return JsonResponse({'code': 10305, 'error': 'topic_id is error or you haven`t limit'})
