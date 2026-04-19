from django.urls import path
from . import views

app_name = 'hopitaux'

urlpatterns = [
    # Tableau de bord principal de l'hôpital
    path('dashboard/', views.dashboard_hopital, name='dashboard'),
    
    # Formulaire de nouvelle demande urgente
    path('creer-demande/', views.creer_demande, name='creer_demande'),
]