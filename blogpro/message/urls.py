from . import views
from django.urls import path

urlpatterns = [
    path('<int:topic_id>', views.message_view)
]
