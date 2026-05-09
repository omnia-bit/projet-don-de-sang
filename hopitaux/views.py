from django.shortcuts import render, redirect, get_object_or_404
from .models import DemandeSang, HopitalProfile, CampagneCollecte, StockSang
from .forms import DemandeSangForm, CampagneCollecteForm, StockSangForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@login_required
def envoyer_email_donneur(request, pk):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')

    if request.method == 'POST':
        email_dest = request.POST.get('email')
        sujet = request.POST.get('sujet', "Contact Urgent - BloodConnect")
        message_body = request.POST.get('message')
        
        try:
            send_mail(
                sujet,
                f"Message de l'hôpital {hopital.nom} :\n\n{message_body}\n\nCordialement,\nL'équipe BloodConnect",
                settings.DEFAULT_FROM_EMAIL,
                [email_dest],
                fail_silently=False,
            )
            messages.success(request, f"Email envoyé avec succès à {email_dest}.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi : {str(e)}")
            
    return redirect(request.META.get('HTTP_REFERER', 'hopitaux:dashboard'))

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
        'demandes_actives_count': demandes.filter(statut='active').count(),
        'campagnes_count': campagnes.count(),
        'stock_total': stock_total,
        'stocks': stocks,
        'alert_stock': alertes_penurie.exists(),
        'groupes_critiques': ", ".join([s.groupe_sanguin for s in alertes_penurie]),
        'today': timezone.now(),
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
    
    # Enrichir les objets stock avec des informations visuelles pour le dashboard
    for s in stocks:
        s.pourcentage = min(round((s.quantite_poches / 50) * 100), 100)
        if s.quantite_poches < 5:
            s.status_class = "bg-critical"
        elif s.quantite_poches < 15:
            s.status_class = "bg-low"
        else:
            s.status_class = "bg-optimal"
    
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
    
    hopital.refresh_from_db()
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

    hopital.refresh_from_db()
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

from django.http import JsonResponse
from donneurs.models import Don, DonneurProfile
from django.utils import timezone

@login_required
def scanner_qr(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')
    return render(request, 'hopitaux/scanner.html', {'titre_page': "Scanner Check-in"})

@login_required
def liste_demandes_hopital(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')
    demandes = DemandeSang.objects.filter(hopital=hopital).order_by('-date_publication')
    return render(request, 'hopitaux/liste_demandes.html', {'demandes': demandes, 'titre_page': "Nos Demandes"})

@login_required
def historique_dons_hopital(request):
    hopital = _get_hopital(request.user)
    if not hopital: return redirect('accounts:login')
    dons = Don.objects.filter(hopital=hopital).select_related('donneur__user').order_by('-date_don')
    return render(request, 'hopitaux/historique_dons.html', {'dons': dons, 'titre_page': "Historique des Collectes"})

@login_required
def process_scan(request):
    hopital = _get_hopital(request.user)
    if not hopital:
        return JsonResponse({'success': False, 'error': 'Accès non autorisé.'})

    uuid_scanne = request.GET.get('uuid') or request.POST.get('uuid')
    check_only = request.GET.get('check_only') == '1'
    
    try:
        donneur = DonneurProfile.objects.get(qr_code_uuid=uuid_scanne)
        
        if check_only:
            return JsonResponse({
                'success': True,
                'donneur': donneur.user.username,
                'groupe': donneur.groupe_sanguin
            })

        if request.method != 'POST':
             return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

        signature = request.POST.get('signature')
        
        # Création du don avec signature
        don = Don.objects.create(
            donneur=donneur,
            hopital=hopital,
            date_don=timezone.now().date(),
            quantite=450,
            lieu=hopital.nom,
            observations="Validé par signature électronique lors du check-in",
            signature_donneur=signature
        )
        
        return JsonResponse({
            'success': True, 
            'donneur': donneur.user.username,
            'message': f"Le don de {donneur.user.username} a été validé et signé avec succès !"
        })
    except DonneurProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Donneur non trouvé.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
