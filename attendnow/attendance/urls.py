from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('sign_in/', views.sign_in_view, name='sign_in'),
    path('sign_up/', views.sign_up_view, name='sign_up'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('submit_attendance/', views.submit_attendance, name='submit_attendance'),
    path('facial_recognition/', views.facial_recognition, name='facial_recognition'),


]
