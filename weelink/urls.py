from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
    path('api/chat/', include('chat.urls')),
    path('admin/', admin.site.urls),

]
