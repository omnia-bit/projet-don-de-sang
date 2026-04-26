from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    # exemple
    path('', views.index, name='accounts_home'),

    path('connexion/', views.custom_login, name='login'),

    path('register/', views.register, name='register'),

    path('logout/', views.logout_view, name='logout'),

    path('donneur/dashboard/', views.dashboard_donneur, name='dashboard_donneur'),
    path('hopital/dashboard/', views.dashboard_hopital, name='dashboard_hopital'),
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),

    path('modifier-profil/', views.modifier_profil, name='modifier_profil'),
]