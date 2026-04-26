from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),

    path('register/', views.register, name='register'),

    path('logout/', views.custom_login, name='logout'),

    path('donneur/dashboard/', views.dashboard_donneur, name='dashboard_donneur'),
    path('hopital/dashboard/', views.dashboard_hopital, name='dashboard_hopital'),
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
]