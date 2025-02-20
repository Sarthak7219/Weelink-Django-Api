# chat/api_urls.py
from django.urls import path
from chat.views import get_or_create_thread, get_thread_messages, get_display_threads

urlpatterns = [
    path('create_thread/', get_or_create_thread),
    path('display_threads/', get_display_threads),
    path('threads/<int:thread_id>/', get_thread_messages, name='get_thread_messages'),
]
