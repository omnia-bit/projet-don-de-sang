from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, DonneurProfile, HopitalProfile
from hopitaux.models import DemandeSang, CampagneCollecte, StockSang
from donneurs.models import Don
from django.db.models import Sum

def dashboard_admin(request):
    # Statistiques globales
    stats = {
        'total_donneurs': DonneurProfile.objects.count(),
        'total_hopitaux': HopitalProfile.objects.count(),
        'hopitaux_valides': HopitalProfile.objects.filter(valide=True).count(),
        'hopitaux_en_attente': HopitalProfile.objects.filter(valide=False).count(),
        'total_demandes': DemandeSang.objects.count(),
        'demandes_actives': DemandeSang.objects.filter(est_resolue=False).count(),
        'total_dons': Don.objects.count(),
        'volume_sang': Don.objects.aggregate(Sum('quantite'))['quantite__sum'] or 0,
    }
    
    # Statistiques par groupe sanguin pour le graphique
    stock_par_groupe = StockSang.objects.values('groupe_sanguin').annotate(total=Sum('quantite_poches'))
    labels_stock = [s['groupe_sanguin'] for s in stock_par_groupe]
    data_stock = [s['total'] for s in stock_par_groupe]

    # Dernières demandes
    dernieres_demandes = DemandeSang.objects.all().order_by('-date_publication')[:5]
    
    # Dernières campagnes
    dernieres_campagnes = CampagneCollecte.objects.all().order_by('-date_debut')[:5]

    context = {
        'stats': stats,
        'labels_stock': labels_stock,
        'data_stock': data_stock,
        'dernieres_demandes': dernieres_demandes,
        'dernieres_campagnes': dernieres_campagnes,
        'titre_page': "Tableau de Bord National"
    }
    return render(request, 'administration/dashboard.html', context)

def valider_hopitaux(request):
    hopitaux_en_attente = HopitalProfile.objects.filter(valide=False)
    hopitaux_valides = HopitalProfile.objects.filter(valide=True)
    
    context = {
        'en_attente': hopitaux_en_attente,
        'valides': hopitaux_valides,
        'titre_page': "Validation des Comptes Hospitaliers"
    }
    return render(request, 'administration/validation_hopitaux.html', context)

def action_validation_hopital(request, pk, action):
    hopital = get_object_or_404(HopitalProfile, pk=pk)
    if action == 'valider':
        hopital.valide = True
    elif action == 'suspendre':
        hopital.valide = False
    hopital.save()
    return redirect('administration:validation_hopitaux')
