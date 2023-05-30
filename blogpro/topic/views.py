import json

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from tools.login_dec import login_check, get_user_by_request
from django.utils.decorators import method_decorator
from .models import Topic
from user.models import Userprofile


# Create your views here.
# 异常码10300-10399
class TopicViews(View):

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
        return JsonResponse({'code': 200})

    def get(self, request, author_id):
        try:
            author = Userprofile.objects.get(username=author_id)
        except Exception as e:
            result = {'code': 10302, 'error': 'the username is error~'}
            return JsonResponse(result)

        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor
        category = request.GET.get('category')
        if category:
            if visitor_name == author_id:
                author_topics = Topic.objects.filter(author=author_id,category=category)
            else:
                author_topics = Topic.objects.filter(author=author_id, limit='public',category=category)
        else:
            if visitor_name == author_id:
                author_topics = Topic.objects.filter(author=author_id)
            else:
                author_topics = Topic.objects.filter(author=author_id, limit='public')
        result = self.make_topics_res(author, author_topics)
        return JsonResponse(result)
