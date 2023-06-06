from django.db import models
from user.models import Userprofile
from topic.models import Topic


class Message(models.Model):
    content = models.CharField(max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    parent_message = models.IntegerField(verbose_name='回复的留言id')
    publisher = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, models.CASCADE)
