from django.contrib import admin

from .models import (Question, Answer, UserProfile)

admin.site.site_header = 'ChatBot Admin'

admin.site.register(Question)
admin.site.register(Answer)

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display=(
        'user',
    )
    list_display_links = list_display