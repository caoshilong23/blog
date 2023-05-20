from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogpro.settings')

app = Celery('blogpro')

app.conf.update(
    BROKER_URL='redis://:@127.0.0.1:6379/1'
)
# 自动在注册的应用下寻找加载worker函数
app.autodiscover_tasks(settings.INSTALLED_APPS)
