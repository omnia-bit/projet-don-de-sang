from django.urls import path
from . import views

urlpatterns = [
    # exemple
    path('', views.index, name='accounts_home'),
    path('connexion/', views.connexion, name='login'), 
]