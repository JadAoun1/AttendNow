# attendnow/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('attendance.urls')),  # Include attendance app URLs
    path('', include('attendance.urls')),  # Include attendance app URLs
    path('attendance/', include('attendance.urls')),  # Adjust the app name if different
    path('', include('attendance.urls')),


]
