from django.shortcuts import render, redirect, get_object_or_404
from .models import DemandeSang, HopitalProfile, CampagneCollecte, StockSang
from .forms import DemandeSangForm, CampagneCollecteForm, StockSangForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def _get_hopital(user):
    try:
        return user.hopital_profile
    except AttributeError:
        return None

# Vue du tableau de bord pour l'établissement hospitalier
@login_required
def dashboard_hopital(request):
    hopital = _get_hopital(request.user)
    if not hopital:
        messages.error(request, "Accès réservé aux hôpitaux.")
        return redirect('accounts:login')

    demandes = DemandeSang.objects.filter(hopital=hopital).order_by('-date_publication')
    campagnes = CampagneCollecte.objects.filter(hopital=hopital).order_by('-date_debut')
    
    # Stock par groupe pour ce hôpital
    stocks = StockSang.objects.filter(hopital=hopital)
    stock_total = stocks.aggregate(Sum('quantite_poches'))['quantite_poches__sum'] or 0
    
    # Alertes de pénurie (seuil < 5 poches)
    alertes_penurie = stocks.filter(quantite_poches__lt=5)
    
    context = {
        'demandes': demandes,
        'campagnes_count': campagnes.count(),
        'stock_total': stock_total,
        'stocks': stocks,
        'alertes_penurie': alertes_penurie,
        'titre_page': "Tableau de Bord Hospitalier"
    }
    return render(request, 'hopitaux/dashboard.html', context)

# Gestion du stock de sang
@login_required
def gestion_stock(request):
    hopital = _get_hopital(request.user)
    if not hopital:
        return redirect('accounts:login')

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
            messages.success(request, f"Stock pour le groupe {groupe} mis à jour : {quantite} poches.")
            return redirect('hopitaux:gestion_stock')
    else:
        form = StockSangForm()
        
    return render(request, 'hopitaux/gestion_stock.html', {
        'form': form,
        'stocks': stocks,
        'titre_page': "Gestion des Stocks de Sang"
    })

# Vue pour créer une nouvelle demande urgente
@login_required
def creer_demande(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')
    
    if not hopital.valide:
        messages.error(request, "⚠️ Votre compte n'est pas encore validé par l'administrateur. Publication impossible.")
        return redirect('hopitaux:dashboard')

    if request.method == 'POST':
        form = DemandeSangForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.hopital = hopital
            demande.save()
            messages.success(request, "Demande urgente publiée avec succès.")
            return redirect('hopitaux:dashboard')
    else:
        form = DemandeSangForm()
    
    return render(request, 'hopitaux/creer_demande.html', {'form': form, 'titre_page': "Nouvelle Demande Urgente"})

@login_required
def modifier_demande(request, pk):
    hopital = _get_hopital(request.user)
    demande = get_object_or_404(DemandeSang, pk=pk, hopital=hopital)
    
    if request.method == 'POST':
        form = DemandeSangForm(request.POST, instance=demande)
        if form.is_valid():
            form.save()
            messages.success(request, "La demande a été mise à jour.")
            return redirect('hopitaux:dashboard')
    else:
        form = DemandeSangForm(instance=demande)
    
    return render(request, 'hopitaux/creer_demande.html', {'form': form, 'titre_page': "Modifier la Demande"})

@login_required
def cloturer_demande(request, pk):
    hopital = _get_hopital(request.user)
    demande = get_object_or_404(DemandeSang, pk=pk, hopital=hopital)
    demande.statut = 'cloturee'
    demande.save()
    messages.info(request, "La demande a été clôturée.")
    return redirect('hopitaux:dashboard')

@login_required
def voir_reponses_demande(request, pk):
    hopital = _get_hopital(request.user)
    demande = get_object_or_404(DemandeSang, pk=pk, hopital=hopital)
    reponses = demande.reponses.all().select_related('donneur__user')
    
    return render(request, 'hopitaux/voir_reponses.html', {
        'demande': demande,
        'reponses': reponses,
        'titre_page': f"Réponses pour {demande.groupe_sanguin}"
    })

# Liste des campagnes de l'hôpital
@login_required
def liste_campagnes(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')

    campagnes = CampagneCollecte.objects.filter(hopital=hopital).order_by('-date_debut')
    return render(request, 'hopitaux/liste_campagnes.html', {'campagnes': campagnes, 'titre_page': "Nos Campagnes"})

# Créer une nouvelle campagne
@login_required
def creer_campagne(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')

    if not hopital.valide:
        messages.error(request, "⚠️ Votre compte n'est pas encore validé par l'administrateur. Publication impossible.")
        return redirect('hopitaux:dashboard')

    if request.method == 'POST':
        form = CampagneCollecteForm(request.POST)
        if form.is_valid():
            campagne = form.save(commit=False)
            campagne.hopital = hopital
            campagne.save()
            messages.success(request, "Campagne créée avec succès.")
            return redirect('hopitaux:liste_campagnes')
    else:
        form = CampagneCollecteForm()
    
    return render(request, 'hopitaux/creer_campagne.html', {'form': form, 'titre_page': "Organiser une Campagne"})

@login_required
def modifier_campagne(request, pk):
    hopital = _get_hopital(request.user)
    campagne = get_object_or_404(CampagneCollecte, pk=pk, hopital=hopital)
    
    if request.method == 'POST':
        form = CampagneCollecteForm(request.POST, instance=campagne)
        if form.is_valid():
            form.save()
            messages.success(request, "La campagne a été mise à jour.")
            return redirect('hopitaux:liste_campagnes')
    else:
        form = CampagneCollecteForm(instance=campagne)
    
    return render(request, 'hopitaux/creer_campagne.html', {'form': form, 'titre_page': "Modifier la Campagne"})

@login_required
def supprimer_campagne(request, pk):
    hopital = _get_hopital(request.user)
    campagne = get_object_or_404(CampagneCollecte, pk=pk, hopital=hopital)
    campagne.delete()
    messages.warning(request, "La campagne a été supprimée.")
    return redirect('hopitaux:liste_campagnes')
