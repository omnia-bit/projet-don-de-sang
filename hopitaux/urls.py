from django.urls import path
from . import views

app_name = 'hopitaux'

urlpatterns = [
    # Tableau de bord principal de l'hôpital
    path('dashboard/', views.dashboard_hopital, name='dashboard'),
]