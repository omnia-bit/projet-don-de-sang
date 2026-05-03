from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse

from accounts.models import DonneurProfile, HopitalProfile
from .models import Don, ReponseAppel, InscriptionCampagne
from .forms import DonForm, ReponseAppelForm
from hopitaux.models import DemandeSang, CampagneCollecte

COMPATIBILITE = {
    'O-':  ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+':  ['O+', 'A+', 'B+', 'AB+'],
    'A-':  ['A-', 'A+', 'AB-', 'AB+'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B-', 'B+', 'AB-', 'AB+'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}


def _get_donneur(request):
    """Retourne le DonneurProfile lié à request.user, ou None."""
    try:
        return DonneurProfile.objects.get(user=request.user)
    except DonneurProfile.DoesNotExist:
        return None


def _calcul_eligibilite(donneur):
    """
    Retourne (est_eligible: bool, prochaine_date: date | None).
    Règle : 56 jours (homme) / 84 jours (femme).
    """
    delai = 84 if getattr(donneur, 'sexe', 'M') == 'F' else 56
    dernier = Don.objects.filter(donneur=donneur).order_by('-date_don').first()
    if dernier is None:
        return True, None
    prochaine = dernier.date_don + timedelta(days=delai)
    return timezone.now().date() >= prochaine, prochaine


def _get_appels(donneur):
    """Récupère les demandes urgentes compatibles."""
    groupes = COMPATIBILITE.get(donneur.groupe_sanguin, [donneur.groupe_sanguin])
    return DemandeSang.objects.filter(
        groupe_sanguin__in=groupes,
        statut='active'
    ).select_related('hopital').order_by('-date_publication')
# TABLEAU DE BORD
@login_required
def dashboard(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable. Contactez l'administrateur.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)
    dons_recents  = Don.objects.filter(donneur=donneur).order_by('-date_don')[:5]
    total_dons    = Don.objects.filter(donneur=donneur).count()
    appels_compat = list(_get_appels(donneur))[:3]
    
    # Rappel des inscriptions aux campagnes (Point 3.4)
    prochaines_campagnes = InscriptionCampagne.objects.filter(
        donneur=donneur, 
        campagne__date_fin__gte=timezone.now()
    ).select_related('campagne')[:3]

    # Calcul barre de progression
    progression   = 100
    jours_restants = 0
    if not est_eligible and prochaine_date:
        dernier = Don.objects.filter(donneur=donneur).order_by('-date_don').first()
        delai   = 84 if getattr(donneur, 'sexe', 'M') == 'F' else 56
        jours_passes   = (timezone.now().date() - dernier.date_don).days
        progression    = min(int((jours_passes / delai) * 100), 99)
        jours_restants = max((prochaine_date - timezone.now().date()).days, 0)

    return render(request, 'donneurs/dashboard.html', {
        'donneur':        donneur,
        'est_eligible':   est_eligible,
        'prochaine_date': prochaine_date,
        'progression':    progression,
        'jours_restants': jours_restants,
        'dons_recents':   dons_recents,
        'total_dons':     total_dons,
        'appels_compatibles': appels_compat,
        'prochaines_campagnes': prochaines_campagnes,
    })
# HISTORIQUE DES DONS
@login_required
def historique_dons(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    dons      = Don.objects.filter(donneur=donneur).order_by('-date_don')
    total_ml  = sum(d.quantite for d in dons)

    return render(request, 'donneurs/historique_dons.html', {
        'donneur':    donneur,
        'dons':       dons,
        'total_dons': dons.count(),
        'total_ml':   total_ml,
    })
# ENREGISTRER UN DON
@login_required
def enregistrer_don(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)
    if not est_eligible:
        messages.warning(
            request,
            f"Vous n'êtes pas encore éligible. Prochaine date possible : {prochaine_date}."
        )
        return redirect('donneurs:dashboard')

    if request.method == 'POST':
        form = DonForm(request.POST)
        if form.is_valid():
            don          = form.save(commit=False)
            don.donneur  = donneur
            don.save()
            messages.success(request, "✅ Votre don a été enregistré avec succès !")
            return redirect('donneurs:historique_dons')
    else:
        form = DonForm()

    return render(request, 'donneurs/enregistrer_don.html', {
        'form':    form,
        'donneur': donneur,
    })
# APPELS URGENTS
@login_required
def appels_urgents(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)
    appels           = _get_appels(donneur)
    groupes_compat   = COMPATIBILITE.get(donneur.groupe_sanguin, [donneur.groupe_sanguin])
    
    # Récupérer les IDs des demandes auxquelles le donneur a déjà répondu
    reponses_ids     = list(
        ReponseAppel.objects.filter(donneur=donneur).values_list('demande_id', flat=True)
    )

    return render(request, 'donneurs/appels_urgents.html', {
        'donneur':            donneur,
        'appels':             appels,
        'est_eligible':       est_eligible,
        'prochaine_date':     prochaine_date,
        'reponses_ids':       reponses_ids,
        'groupes_compatibles': groupes_compat,
    })
# RÉPONDRE À UN APPEL
@login_required
def repondre_appel(request, demande_id):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)
    if not est_eligible:
        messages.warning(request, f"Vous n'êtes pas éligible avant le {prochaine_date}.")
        return redirect('donneurs:appels_urgents')

    demande = get_object_or_404(DemandeSang, id=demande_id, statut='active')

    if ReponseAppel.objects.filter(donneur=donneur, demande=demande).exists():
        messages.info(request, "Vous avez déjà répondu à cet appel.")
        return redirect('donneurs:appels_urgents')

    if request.method == 'POST':
        form = ReponseAppelForm(request.POST)
        if form.is_valid():
            reponse            = form.save(commit=False)
            reponse.donneur    = donneur
            reponse.demande    = demande
            reponse.save()
            messages.success(
                request,
                "✅ Votre intention de don a été transmise. L'hôpital vous contactera bientôt."
            )
            return redirect('donneurs:appels_urgents')
    else:
        form = ReponseAppelForm()

    return render(request, 'donneurs/repondre_appel.html', {
        'form':    form,
        'demande': demande,
        'donneur': donneur,
    })
# GESTION DES CAMPAGNES (NOUVEAU)
@login_required
def liste_campagnes(request):
    donneur = _get_donneur(request)
    if not donneur: return redirect('accueil')

    campagnes = CampagneCollecte.objects.filter(date_fin__gte=timezone.now()).order_by('date_debut')
    # On marque les campagnes auxquelles le donneur est déjà inscrit
    inscriptions_ids = InscriptionCampagne.objects.filter(donneur=donneur).values_list('campagne_id', flat=True)

    return render(request, 'donneurs/liste_campagnes.html', {
        'campagnes': campagnes,
        'inscriptions_ids': list(inscriptions_ids)
    })

@login_required
def sinscrire_campagne(request, campagne_id):
    donneur = _get_donneur(request)
    campagne = get_object_or_404(CampagneCollecte, id=campagne_id)

    # Vérification si déjà inscrit
    if InscriptionCampagne.objects.filter(donneur=donneur, campagne=campagne).exists():
        messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
        return redirect('donneurs:liste_campagnes')

    # Génération des créneaux horaires
    creneaux = []
    duree_totale = (campagne.date_fin - campagne.date_debut).total_seconds() / 3600
    intervalle = max(duree_totale / campagne.nb_creneaux, 0.5) 
    
    capacité_par_creneau = max(campagne.capacite_totale // campagne.nb_creneaux, 1)

    current_time = campagne.date_debut
    for i in range(campagne.nb_creneaux):
        fin_creneau = current_time + timedelta(hours=intervalle)
        label = f"{current_time.strftime('%H:%M')} - {fin_creneau.strftime('%H:%M')}"
        
        count = InscriptionCampagne.objects.filter(campagne=campagne, creneau_horaire=label).count()
        disponible = count < capacité_par_creneau
        
        creneaux.append({
            'label': label,
            'disponible': disponible,
            'places_restantes': capacité_par_creneau - count
        })
        current_time = fin_creneau

    if request.method == 'POST':
        choix = request.POST.get('creneau')
        if choix:
            count = InscriptionCampagne.objects.filter(campagne=campagne, creneau_horaire=choix).count()
            if count < capacité_par_creneau:
                InscriptionCampagne.objects.create(
                    donneur=donneur,
                    campagne=campagne,
                    creneau_horaire=choix
                )
                messages.success(request, f"✅ Inscription confirmée pour le créneau {choix} !")
                return redirect('donneurs:dashboard')
            else:
                messages.error(request, "Désolé, ce créneau est désormais complet.")
        else:
            messages.error(request, "Veuillez choisir un créneau horaire.")

    return render(request, 'donneurs/sinscrire_campagne.html', {
        'campagne': campagne,
        'creneaux': creneaux
    })

@login_required
def toggle_disponibilite(request):
    donneur = _get_donneur(request)
    if not donneur: return redirect('accueil')
    
    donneur.actif = not donneur.actif
    donneur.save()
    
    status = "activé" if donneur.actif else "désactivé (indisponible)"
    messages.info(request, f"Votre statut a été mis à jour : compte {status}.")
    return redirect('donneurs:dashboard')

def index(request):
    return HttpResponse("Page donneurs fonctionne")