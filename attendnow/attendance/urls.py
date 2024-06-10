from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('signin/', views.sign_in_view, name='signin'),
    path('signup/', views.sign_up_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('settings/', views.settings_view, name='settings'),
]
