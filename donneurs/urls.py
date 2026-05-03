from django.urls import path
from . import views

app_name = 'donneurs'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('enregistrer-don/', views.enregistrer_don, name='enregistrer_don'),
    path('historique/', views.historique_dons, name='historique_dons'),
    path('appels-urgents/', views.appels_urgents, name='appels_urgents'),
    path('repondre-appel/<int:demande_id>/', views.repondre_appel, name='repondre_appel'),
    path('campagnes/', views.liste_campagnes, name='liste_campagnes'),
    path('campagnes/inscription/<int:campagne_id>/', views.sinscrire_campagne, name='sinscrire_campagne'),
    path('profil/toggle-status/', views.toggle_disponibilite, name='toggle_status'),
]