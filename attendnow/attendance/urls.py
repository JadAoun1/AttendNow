from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .jwt_views import urlpatterns as jwt_urls
from .views import attendance_records


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
    path('api/', include(jwt_urls)),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('role_selection/', views.role_selection, name='role_selection'),
    path('sign_in/student/', views.sign_in_student, name='sign_in_student'),
    path('sign_in/admin/', views.sign_in_admin, name='sign_in_admin'), 
    path('sign_in/student/', views.sign_in_student, name='sign_in_student'),
    path('sign_in/employee/', views.sign_in_employee, name='sign_in_employee'),
    path('overall_attendance/', views.overall_attendance, name='overall_attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('add_view_groups/', views.add_view_groups, name='add_view_groups'),
    path('messages/', views.messages, name='messages'),
    path('calendar/', views.calendar, name='calendar'),
    path('activity/', views.activity, name='activity'),
    path('settings/account/', views.account_settings, name='account_settings'),
    path('settings/notifications/', views.notifications, name='notifications'),
    path('settings/password_reset/', views.password_reset, name='forgot_password'),
    path('settings/app/', views.app_settings, name='app_settings'),
    path('settings/privacy/', views.privacy_settings, name='privacy_settings'),
    path('settings/support/', views.contact_support, name='contact_support'),
    path('attendance-records/', attendance_records, name='attendance_records'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_code/', views.reset_password_code, name='reset_password_code'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),


]
