from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse

from accounts.models import DonneurProfile, HopitalProfile
from .models import Don, ReponseAppel, InscriptionCampagne
from .forms import DonForm, ReponseAppelForm
from hopitaux.models import DemandeSang, CampagneCollecte
from .badges import get_badges_donneur, get_classement_ville

import json
import urllib.request
import urllib.parse
from django.conf import settings

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
    try:
        return DonneurProfile.objects.get(user=request.user)
    except DonneurProfile.DoesNotExist:
        return None


def _calcul_eligibilite(donneur):
    delai = 84 if getattr(donneur, 'sexe', 'M') == 'F' else 56
    dernier = Don.objects.filter(donneur=donneur).order_by('-date_don').first()
    if dernier is None:
        return True, None
    prochaine = dernier.date_don + timedelta(days=delai)
    return timezone.now().date() >= prochaine, prochaine


def _get_appels(donneur):
    groupes = COMPATIBILITE.get(donneur.groupe_sanguin, [donneur.groupe_sanguin])
    return DemandeSang.objects.filter(
        groupe_sanguin__in=groupes,
        statut='active'
    ).select_related('hopital').order_by('-date_publication')


# ───────────────────────────────────────────────────────────────
# TABLEAU DE BORD DONNEUR
# ───────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable. Contactez l'administrateur.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)
    dons_recents = Don.objects.filter(donneur=donneur).order_by('-date_don')[:5]
    total_dons   = Don.objects.filter(donneur=donneur).count()

    # Liste texte : 3 premiers appels compatibles
    appels_complets = _get_appels(donneur)
    appels_compat   = list(appels_complets)[:3]

    # ── CARTE : TOUS les hôpitaux validés avec coordonnées GPS réelles ──────────
    # On prend HopitalProfile directement (coordonnées saisies via register.html).
    # On n'exige PAS un appel actif — l'hôpital doit juste être validé et avoir lat/lng.
    hopitaux_valides = HopitalProfile.objects.filter(
        valide=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).select_related('user')

    map_data = []
    for h in hopitaux_valides:
        # Cherche si cet hôpital a un appel actif compatible (optionnel, pour info)
        appel = DemandeSang.objects.filter(
            hopital=h,
            statut='active'
        ).order_by('-date_publication').first()

        map_data.append({
            'nom':     h.nom,
            'ville':   h.ville,
            'adresse': h.adresse or h.ville,
            'lat':     float(h.latitude),   # ← coordonnée réelle saisie à l'inscription
            'lng':     float(h.longitude),  # ← coordonnée réelle saisie à l'inscription
            'poches':  appel.quantite_necessaire if appel else 0,
            'groupe':  appel.groupe_sanguin if appel else '—',
            'has_appel': appel is not None,
        })

    # Position du donneur (Sfax par défaut — remplace par géocodage si besoin)
    donneur_pos = {'lat': 34.7625, 'lng': 10.7441}

    prochaines_campagnes = InscriptionCampagne.objects.filter(
        donneur=donneur,
        campagne__date_fin__gte=timezone.now()
    ).select_related('campagne')[:3]

    progression    = 100
    jours_restants = 0
    if not est_eligible and prochaine_date:
        dernier    = Don.objects.filter(donneur=donneur).order_by('-date_don').first()
        delai      = 84 if getattr(donneur, 'sexe', 'M') == 'F' else 56
        jours_passes = (timezone.now().date() - dernier.date_don).days
        progression    = min(int((jours_passes / delai) * 100), 99)
        jours_restants = max((prochaine_date - timezone.now().date()).days, 0)

    badges_obtenus, _ = get_badges_donneur(donneur)
    vies_sauvees = total_dons * 3

    return render(request, 'donneurs/dashboard.html', {
        'donneur':              donneur,
        'est_eligible':         est_eligible,
        'prochaine_date':       prochaine_date,
        'progression':          progression,
        'jours_restants':       jours_restants,
        'dons_recents':         dons_recents,
        'total_dons':           total_dons,
        'appels_compatibles':   appels_compat,
        'prochaines_campagnes': prochaines_campagnes,
        'map_data_json':        json.dumps(map_data, cls=DjangoJSONEncoder),
        'donneur_pos':          donneur_pos,
        'badges_obtenus': badges_obtenus,
        'vies_sauvees':   vies_sauvees,
    })


# HISTORIQUE DES DONS
@login_required
def historique_dons(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    dons     = Don.objects.filter(donneur=donneur).order_by('-date_don')
    total_ml = sum(d.quantite for d in dons)

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
            don         = form.save(commit=False)
            don.donneur = donneur
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
    appels         = _get_appels(donneur)
    groupes_compat = COMPATIBILITE.get(donneur.groupe_sanguin, [donneur.groupe_sanguin])

    reponses_ids = list(
        ReponseAppel.objects.filter(donneur=donneur).values_list('demande_id', flat=True)
    )

    return render(request, 'donneurs/appels_urgents.html', {
        'donneur':             donneur,
        'appels':              appels,
        'est_eligible':        est_eligible,
        'prochaine_date':      prochaine_date,
        'reponses_ids':        reponses_ids,
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
            reponse         = form.save(commit=False)
            reponse.donneur = donneur
            reponse.demande = demande
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


# CAMPAGNES
@login_required
def liste_campagnes(request):
    donneur = _get_donneur(request)
    if not donneur:
        return redirect('accueil')

    campagnes        = CampagneCollecte.objects.filter(date_fin__gte=timezone.now()).order_by('date_debut')
    inscriptions_ids = InscriptionCampagne.objects.filter(donneur=donneur).values_list('campagne_id', flat=True)

    return render(request, 'donneurs/liste_campagnes.html', {
        'campagnes':        campagnes,
        'inscriptions_ids': list(inscriptions_ids)
    })


@login_required
def sinscrire_campagne(request, campagne_id):
    donneur = _get_donneur(request)
    campagne = get_object_or_404(CampagneCollecte, id=campagne_id)

    if InscriptionCampagne.objects.filter(
        donneur=donneur,
        campagne=campagne
    ).exists():
        messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
        return redirect('donneurs:liste_campagnes')

    creneaux = []

    duree_totale = (
        campagne.date_fin - campagne.date_debut
    ).total_seconds() / 3600

    intervalle = max(duree_totale / campagne.nb_creneaux, 0.5)

    capacite_par_creneau = max(
        campagne.capacite_totale // campagne.nb_creneaux,
        1
    )

    current_time = campagne.date_debut

    for i in range(campagne.nb_creneaux):

        fin_creneau = current_time + timedelta(hours=intervalle)

        label = (
            f"{current_time.strftime('%H:%M')} - "
            f"{fin_creneau.strftime('%H:%M')}"
        )

        count = InscriptionCampagne.objects.filter(
            campagne=campagne,
            creneau_horaire=label
        ).count()

        places_restantes = max(capacite_par_creneau - count, 0)

        creneaux.append({
            'label': label,
            'disponible': count < capacite_par_creneau,
            'places_restantes': places_restantes
        })

        current_time = fin_creneau

    if request.method == 'POST':

        choix = request.POST.get('creneau')

        if choix:

            count = InscriptionCampagne.objects.filter(
                campagne=campagne,
                creneau_horaire=choix
            ).count()

            if count < capacite_par_creneau:

                InscriptionCampagne.objects.create(
                    donneur=donneur,
                    campagne=campagne,
                    creneau_horaire=choix
                )

                messages.success(
                    request,
                    f"✅ Inscription confirmée pour le créneau {choix} !"
                )

                return redirect('donneurs:dashboard')

            else:
                messages.error(
                    request,
                    "Désolé, ce créneau est désormais complet."
                )

        else:
            messages.error(
                request,
                "Veuillez choisir un créneau horaire."
            )

    return render(request, 'donneurs/sinscrire_campagne.html', {
        'campagne': campagne,
        'creneaux': creneaux
    })


@login_required
def toggle_disponibilite(request):
    donneur = _get_donneur(request)
    if not donneur:
        return redirect('accueil')
    donneur.actif = not donneur.actif
    donneur.save()
    status = "activé" if donneur.actif else "désactivé (indisponible)"
    messages.info(request, f"Votre statut a été mis à jour : compte {status}.")
    return redirect('donneurs:dashboard')


# CHATBOT IA — Cohere
@login_required
def chatbot_ia(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    est_eligible, prochaine_date = _calcul_eligibilite(donneur)

    if request.method == 'POST':
        try:
            body       = json.loads(request.body)
            question   = body.get('message', '').strip()
            conv_id    = body.get('conv_id')
            if not question:
                return JsonResponse({'erreur': 'Message vide.'}, status=400)

            delai = 84 if getattr(donneur, 'sexe', 'M') == 'F' else 56

            system_prompt = f"""Tu es un assistant spécialisé en don de sang pour DonSang (Tunisie). Réponds en français, de façon concise (3-4 phrases max).
Profil: {donneur.user.first_name or donneur.user.username}, groupe {donneur.groupe_sanguin}, {'femme' if getattr(donneur, 'sexe', 'M') == 'F' else 'homme'}, délai {delai}j, {'éligible' if est_eligible else f'prochain don le {prochaine_date}'}, {Don.objects.filter(donneur=donneur).count()} dons effectués."""

            payload = json.dumps({
                "message": question,
                "model":   "command-a-03-2025",
                "preamble": system_prompt,
                "max_tokens": 200,
                "temperature": 0.7
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://api.cohere.com/v1/chat',
                data=payload,
                headers={
                    'Content-Type':  'application/json',
                    'Authorization': f'Bearer {settings.COHERE_API_KEY}'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                data       = json.loads(response.read().decode('utf-8'))
                reponse_ia = data['text'].strip()

            if not reponse_ia:
                reponse_ia = "Je n'ai pas pu générer une réponse, veuillez réessayer."

            from .models import ConversationChatbot, MessageChatbot
            if conv_id:
                try:
                    conversation = ConversationChatbot.objects.get(id=conv_id, donneur=donneur)
                except ConversationChatbot.DoesNotExist:
                    conversation = ConversationChatbot.objects.create(donneur=donneur, titre=question[:80])
            else:
                conversation = ConversationChatbot.objects.create(donneur=donneur, titre=question[:80])

            MessageChatbot.objects.create(conversation=conversation, role='user',      contenu=question)
            MessageChatbot.objects.create(conversation=conversation, role='assistant', contenu=reponse_ia)

            return JsonResponse({'reponse': reponse_ia, 'conv_id': conversation.id})

        except Exception as e:
            import traceback
            return JsonResponse({'erreur': str(e), 'detail': traceback.format_exc()}, status=500)

    return render(request, 'donneurs/chatbot.html', {
        'donneur':        donneur,
        'est_eligible':   est_eligible,
        'prochaine_date': prochaine_date,
    })


@login_required
def historique_conversations(request):
    donneur = _get_donneur(request)
    if donneur is None:
        return redirect('accueil')
    from .models import ConversationChatbot
    conversations = ConversationChatbot.objects.filter(donneur=donneur)
    return render(request, 'donneurs/historique_conversations.html', {
        'donneur':       donneur,
        'conversations': conversations,
    })


@login_required
def detail_conversation(request, conv_id):
    donneur = _get_donneur(request)
    if donneur is None:
        return redirect('accueil')
    from .models import ConversationChatbot
    conversation = get_object_or_404(ConversationChatbot, id=conv_id, donneur=donneur)
    return render(request, 'donneurs/detail_conversation.html', {
        'donneur':       donneur,
        'conversation':  conversation,
        'messages_list': conversation.messages.all(),
    })


@login_required
def supprimer_conversation(request, conv_id):
    donneur = _get_donneur(request)
    if donneur is None:
        return redirect('accueil')
    from .models import ConversationChatbot
    conversation = get_object_or_404(ConversationChatbot, id=conv_id, donneur=donneur)
    conversation.delete()
    messages.success(request, "Conversation supprimée.")
    return redirect('donneurs:historique_conversations')


@login_required
def badges(request):
    donneur = _get_donneur(request)
    if donneur is None:
        messages.error(request, "Profil donneur introuvable.")
        return redirect('accueil')

    from .badges import get_badges_donneur, get_classement_ville
    from .models import Don

    badges_obtenus, badges_a_venir = get_badges_donneur(donneur)
    total_dons  = Don.objects.filter(donneur=donneur).count()
    vies_sauvees = total_dons * 3

    ville = donneur.ville or ''
    classement = get_classement_ville(ville, limit=10) if ville else []

    # Rang du donneur courant dans le classement
    rang_ville = '—'
    for item in classement:
        nom_court = donneur.user.first_name or donneur.user.username
        if item['nom'].lower().startswith(nom_court[:2].lower()):
            rang_ville = item['rang']
            break

    return render(request, 'donneurs/badges.html', {
        'donneur':        donneur,
        'badges_obtenus': badges_obtenus,
        'badges_a_venir': badges_a_venir,
        'total_dons':     total_dons,
        'vies_sauvees':   vies_sauvees,
        'classement':     classement,
        'rang_ville':     rang_ville,
    })



def index(request):
    return HttpResponse("Page donneurs fonctionne")