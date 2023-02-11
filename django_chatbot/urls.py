import debug_toolbar

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('chatbot.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
