from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-up/', views.sign_up_view, name='sign_up'),
    path('sign-in/', views.sign_in_view, name='sign_in'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('settings/', views.settings_view, name='settings'),
]
