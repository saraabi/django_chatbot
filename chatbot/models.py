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
    description = models.CharField(max_length=255, blank=True,
        default='a friendly AI assistant')
    prompt = models.TextField(blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
    
    def __str__(self):
        return self.user.get_full_name()

    def get_display_name(self):
        return self.user.get_full_name()

    def build_prompt(self):
        prompt = """The following is a conversation with an \
            AI assistant.\nHuman: Who are you?
            AI: I am {0}""".format(self.description)
        for answer in self.answer_set.all():
            prompt += """
                Human: {0}
                AI: {1}""".format(answer.question.name,
                    answer.text)
        return prompt


class Question(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(UserProfile, 
        on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_training = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return self.name

class Answer(models.Model):

    question = models.ForeignKey(Question, 
        on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    user = models.ForeignKey(UserProfile, 
        on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return 'Response to {}'.format(self.question.name)

    class Meta:
        ordering = ('timestamp',)    