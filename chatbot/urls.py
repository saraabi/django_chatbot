from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from .views import HarvestEmails, Home, CreateAnswer, Chat

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('answer', CreateAnswer.as_view(), name='create_answer'),
    path('emails/', HarvestEmails.as_view(), name='harvest_emails'),
    path('chat/<pk>/', Chat.as_view(), name='chat'),
]
