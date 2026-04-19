from django.shortcuts import render, redirect
from .models import DemandeSang, HopitalProfile
from .forms import DemandeSangForm

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

# Vue pour créer une nouvelle demande urgente
def creer_demande(request):
    if request.method == 'POST':
        form = DemandeSangForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            # Logique temporaire : on récupère le premier hôpital de la base
            # (À remplacer par l'hôpital connecté plus tard)
            hopital = HopitalProfile.objects.first()
            if hopital:
                demande.hopital = hopital
                demande.save()
                return redirect('hopitaux:dashboard')
    else:
        form = DemandeSangForm()
    
    return render(request, 'hopitaux/creer_demande.html', {'form': form})
