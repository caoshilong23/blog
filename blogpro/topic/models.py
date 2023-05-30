from django.db import models
from user.models import Userprofile
# Create your models here.

class Topic(models.Model):

    title = models.CharField(max_length=50,verbose_name='文章标题')
    # tec  no-tec
    category = models.CharField(max_length=20,verbose_name='文章分类')
    # public, private
    limit = models.CharField(max_length=10,verbose_name='文章权限')
    introduce = models.CharField(max_length=50,verbose_name='文章简介')
    content = models.TextField(verbose_name='文章内容')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Userprofile,on_delete=models.CASCADE)

