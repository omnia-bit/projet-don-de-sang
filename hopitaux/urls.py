from django.urls import path
from . import views

app_name = 'hopitaux'

urlpatterns = [
    # Redirection par défaut vers le dashboard 
    path('', views.dashboard_hopital, name='index'),

    # Tableau de bord principal de l'hôpital
    path('dashboard/', views.dashboard_hopital, name='dashboard'),
    
    # Gestion des demandes urgentes
    path('demandes/', views.liste_demandes_hopital, name='liste_demandes'),
    path('demande/creer/', views.creer_demande, name='creer_demande'),
    path('demande/modifier/<int:pk>/', views.modifier_demande, name='modifier_demande'),
    path('demande/cloturer/<int:pk>/', views.cloturer_demande, name='cloturer_demande'),
    path('demande/reponses/<int:pk>/', views.voir_reponses_demande, name='voir_reponses'),

    # Gestion des campagnes
    path('campagnes/', views.liste_campagnes, name='liste_campagnes'),
    path('campagnes/creer/', views.creer_campagne, name='creer_campagne'),
    path('campagnes/modifier/<int:pk>/', views.modifier_campagne, name='modifier_campagne'),
    path('campagnes/supprimer/<int:pk>/', views.supprimer_campagne, name='supprimer_campagne'),

    # Gestion de stock
    path('stock/', views.gestion_stock, name='gestion_stock'),

    # Scanner QR Code et Historique
    path('scanner/', views.scanner_qr, name='scanner_qr'),
    path('scanner/process/', views.process_scan, name='process_scan'),
    path('dons/historique/', views.historique_dons_hopital, name='historique_dons'),
    path('contact/email/<int:pk>/', views.envoyer_email_donneur, name='envoyer_email_donneur'),
]