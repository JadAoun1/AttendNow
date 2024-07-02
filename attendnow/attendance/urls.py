from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('sign_in/', auth_views.LoginView.as_view(template_name='attendance/signIn.html'), name='sign_in'),
    path('sign_up/', views.sign_up_view, name='sign_up'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('submit_attendance/', views.submit_attendance, name='submit_attendance'),
    path('facial_recognition/', views.facial_recognition, name='facial_recognition'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

]