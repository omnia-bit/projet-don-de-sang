from django.urls import path
from . import views

app_name = 'hopitaux'

urlpatterns = [
    # Redirection par défaut vers le dashboard (évite le 404 sur /hopitaux/)
    path('', views.dashboard_hopital, name='index'),

    # Tableau de bord principal de l'hôpital
    path('dashboard/', views.dashboard_hopital, name='dashboard'),
    
    # Formulaire de nouvelle demande urgente
    path('creer-demande/', views.creer_demande, name='creer_demande'),

    # Gestion des campagnes
    path('campagnes/', views.liste_campagnes, name='liste_campagnes'),
    path('campagnes/creer/', views.creer_campagne, name='creer_campagne'),

    # Gestion de stock
    path('stock/', views.gestion_stock, name='gestion_stock'),
]