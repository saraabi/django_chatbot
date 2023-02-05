from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from .views import Home, CreateAnswer, Chat

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('answer', CreateAnswer.as_view(), name='create_answer'),
    path('chat/<pk>', Chat.as_view(), name='chat'),
]
