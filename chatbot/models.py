import uuid as uuid_lib

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_chatbot.storage_backends import PublicMediaStorage

class UserProfile(models.Model):

    uuid = models.UUIDField(db_index=True, 
        default=uuid_lib.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
    
    def __str__(self):
        return self.user.get_full_name()

    def get_display_name(self):
        return self.user.get_full_name()

class Question(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Answer(models.Model):

    question = models.ForeignKey(Question, 
        on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    respondent = models.ForeignKey(UserProfile, 
        on_delete=models.CASCADE)
    
    def __str__(self):
        return 'Response to {}'.format(self.question.name)