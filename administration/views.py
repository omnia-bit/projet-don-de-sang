from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, DonneurProfile, HopitalProfile
from hopitaux.models import DemandeSang, CampagneCollecte, StockSang
from donneurs.models import Don
from django.db.models import Sum

import csv
from django.http import HttpResponse
from django.db.models import Count

from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    # Statistiques globales
    stats = {
        'total_donneurs': DonneurProfile.objects.count(),
        'total_hopitaux': HopitalProfile.objects.count(),
        'hopitaux_valides': HopitalProfile.objects.filter(valide=True).count(),
        'hopitaux_en_attente': HopitalProfile.objects.filter(valide=False).count(),
        'total_demandes': DemandeSang.objects.count(),
        'demandes_actives': DemandeSang.objects.filter(statut='active').count(),
        'total_dons': Don.objects.count(),
        'volume_sang': Don.objects.aggregate(Sum('quantite'))['quantite__sum'] or 0,
    }
    
    # Statistiques par groupe sanguin pour le graphique (Demandes Actives)
    demandes_par_groupe = DemandeSang.objects.filter(statut='active').values('groupe_sanguin').annotate(total=Sum('quantite_necessaire'))
    labels_stock = [s['groupe_sanguin'] for s in demandes_par_groupe]
    data_stock = [s['total'] or 0 for s in demandes_par_groupe]

    # Détection de pénurie nationale (Somme < 20 poches par groupe au niveau national)
    stock_actuel = StockSang.objects.values('groupe_sanguin').annotate(total=Sum('quantite_poches'))
    alertes_penurie = [s for s in stock_actuel if s['total'] < 20]

    # Demandes par ville (Carte simplifiée)
    demandes_par_ville = DemandeSang.objects.filter(statut='active').values('hopital__ville').annotate(total=Count('id')).order_by('-total')

    # Dernières demandes
    dernieres_demandes = DemandeSang.objects.all().order_by('-date_publication')[:5]
    
    # Dernières campagnes
    dernieres_campagnes = CampagneCollecte.objects.all().order_by('-date_debut')[:5]

    context = {
        'stats': stats,
        'labels_stock': labels_stock,
        'data_stock': data_stock,
        'alertes_penurie': alertes_penurie,
        'demandes_par_ville': demandes_par_ville,
        'dernieres_demandes': dernieres_demandes,
        'dernieres_campagnes': dernieres_campagnes,
        'titre_page': "Tableau de Bord National"
    }
    return render(request, 'administration/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def valider_hopitaux(request):
    hopitaux_en_attente = HopitalProfile.objects.filter(valide=False)
    hopitaux_valides = HopitalProfile.objects.filter(valide=True)
    
    context = {
        'en_attente': hopitaux_en_attente,
        'valides': hopitaux_valides,
        'titre_page': "Validation des Comptes Hospitaliers"
    }
    return render(request, 'administration/validation_hopitaux.html', context)

@login_required
@user_passes_test(is_admin)
def action_validation_hopital(request, pk, action):
    hopital = get_object_or_404(HopitalProfile, pk=pk)
    if action == 'valider':
        hopital.valide = True
    elif action == 'suspendre':
        hopital.valide = False
    hopital.save()
    return redirect('administration:validation_hopitaux')

@login_required
@user_passes_test(is_admin)
def export_donneurs_csv(request):
    # Création de la réponse avec le type MIME CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donneurs_bloodconnect.csv"'

    writer = csv.writer(response)
    # En-têtes
    writer.writerow(['Nom d\'utilisateur', 'Email', 'Groupe Sanguin', 'Ville', 'Date d\'inscription'])

    # Données
    donneurs = DonneurProfile.objects.select_related('user').all()
    for d in donneurs:
        writer.writerow([
            d.user.username,
            d.user.email,
            d.groupe_sanguin,
            d.ville,
            d.user.date_joined.strftime('%Y-%m-%d')
        ])

    return response
