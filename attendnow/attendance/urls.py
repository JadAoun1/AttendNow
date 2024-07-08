from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .jwt_views import urlpatterns as jwt_urls

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sign_in/', auth_views.LoginView.as_view(template_name='attendance/signIn.html'), name='sign_in'),
    path('sign_up/', views.sign_up_view, name='sign_up'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('weekly_attendance/', views.weekly_attendance_view, name='weekly_attendance_view'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('submit_attendance/', views.submit_attendance, name='submit_attendance'),
    path('facial_recognition/', views.facial_recognition, name='facial_recognition'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/attend/', views.AttendView.as_view(), name='attend'),
    path('api/weekly_attendance/', views.WeeklyAttendanceView.as_view(), name='weekly_attendance'),
    path('api/', include(jwt_urls)),  # Include JWT URLs under the 'apis/' prefix
]
