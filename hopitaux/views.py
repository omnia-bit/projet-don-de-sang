from django.shortcuts import render
from .models import DemandeSang, HopitalProfile

# Vue du tableau de bord pour l'établissement hospitalier
def dashboard_hopital(request):
    # En phase initiale, nous récupérons toutes les demandes
    # Plus tard, nous filtrerons par l'hôpital connecté
    demandes = DemandeSang.objects.all().order_by('-date_publication')
    
    context = {
        'demandes': demandes,
        'titre_page': "Tableau de Bord Hospitalier"
    }
    return render(request, 'hopitaux/dashboard.html', context)
