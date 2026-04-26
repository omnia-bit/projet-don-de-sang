from django.shortcuts import render, redirect
from .models import DemandeSang, HopitalProfile, CampagneCollecte, StockSang
from .forms import DemandeSangForm, CampagneCollecteForm, StockSangForm
from django.db.models import Sum

# Vue du tableau de bord pour l'établissement hospitalier
def dashboard_hopital(request):
    # En phase initiale, nous récupérons toutes les demandes
    # Plus tard, nous filtrerons par l'hôpital connecté
    demandes = DemandeSang.objects.all().order_by('-date_publication')
    campagnes = CampagneCollecte.objects.all().order_by('-date_debut')
    
    # Stock total
    stock_total = StockSang.objects.aggregate(Sum('quantite_poches'))['quantite_poches__sum'] or 0
    
    context = {
        'demandes': demandes,
        'campagnes_count': campagnes.count(),
        'stock_total': stock_total,
        'titre_page': "Tableau de Bord Hospitalier"
    }
    return render(request, 'hopitaux/dashboard.html', context)

from django.contrib import messages

# Gestion du stock de sang
def gestion_stock(request):
    hopital = HopitalProfile.objects.first() # Temporaire
    
    if not hopital:
        messages.error(request, "Aucun profil d'hôpital trouvé. Veuillez en créer un dans l'administration Django d'abord.")
        return render(request, 'hopitaux/gestion_stock.html', {'stocks': [], 'titre_page': "Gestion des Stocks"})

    stocks = StockSang.objects.filter(hopital=hopital)
    
    if request.method == 'POST':
        form = StockSangForm(request.POST)
        if form.is_valid():
            groupe = form.cleaned_data['groupe_sanguin']
            quantite = form.cleaned_data['quantite_poches']
            
            # Mise à jour ou création
            stock_obj, created = StockSang.objects.update_or_create(
                hopital=hopital,
                groupe_sanguin=groupe,
                defaults={'quantite_poches': quantite}
            )
            messages.success(request, f"Stock pour {groupe} mis à jour.")
            return redirect('hopitaux:gestion_stock')
    else:
        form = StockSangForm()
        
    return render(request, 'hopitaux/gestion_stock.html', {
        'form': form,
        'stocks': stocks,
        'titre_page': "Gestion des Stocks"
    })

# Vue pour créer une nouvelle demande urgente
def creer_demande(request):
    if request.method == 'POST':
        form = DemandeSangForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            hopital = HopitalProfile.objects.first() # Temporaire
            if hopital:
                demande.hopital = hopital
                demande.save()
                return redirect('hopitaux:dashboard')
    else:
        form = DemandeSangForm()
    
    return render(request, 'hopitaux/creer_demande.html', {'form': form})

# Liste des campagnes de l'hôpital
def liste_campagnes(request):
    campagnes = CampagneCollecte.objects.all().order_by('-date_debut')
    return render(request, 'hopitaux/liste_campagnes.html', {'campagnes': campagnes})

# Créer une nouvelle campagne
def creer_campagne(request):
    if request.method == 'POST':
        form = CampagneCollecteForm(request.POST)
        if form.is_valid():
            campagne = form.save(commit=False)
            hopital = HopitalProfile.objects.first() # Temporaire
            if hopital:
                campagne.hopital = hopital
                campagne.save()
                return redirect('hopitaux:liste_campagnes')
    else:
        form = CampagneCollecteForm()
    
    return render(request, 'hopitaux/creer_campagne.html', {'form': form})
