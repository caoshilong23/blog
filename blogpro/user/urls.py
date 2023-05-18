from django.urls import path

from . import views

urlpatterns = [
    path('sms',views.send_sms),
    path('<str:username>', views.UserViews.as_view()),
    path('<str:username>/avatar', views.users_views)
]