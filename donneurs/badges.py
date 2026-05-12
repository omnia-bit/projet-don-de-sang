"""
donneurs/badges.py
Logique de calcul et d'attribution automatique des badges donneur.
"""

from django.utils import timezone
from django.db.models import Min, Max


# ── Définition des badges: liste contenant les badges du système ────────────────────────────────────────────────────
BADGE_DEFINITIONS = [
    {
        'code':        'premier_don',
        'nom':         'Premier Pas',
        'description': 'A effectué son premier don de sang',
        'icone':       '🩸',
        'couleur':     '#E63946',
        'critere':     'Avoir enregistré au moins 1 don',
        'niveau':      'bronze',
    },
    {
        'code':        'donneur_regulier',
        'nom':         'Donneur Régulier',
        'description': 'A effectué 3 dons ou plus',
        'icone':       '🔥',
        'couleur':     '#f59e0b',
        'critere':     '3 dons enregistrés',
        'niveau':      'silver',
    },
    {
        'code':        'heros_sang',
        'nom':         'Héros du Sang',
        'description': 'A effectué 5 dons ou plus',
        'icone':       '💎',
        'couleur':     '#8b5cf6',
        'critere':     '5 dons enregistrés',
        'niveau':      'gold',
    },
    {
        'code':        'repondeur_urgent',
        'nom':         'Répondeur Urgent',
        'description': 'A répondu à au moins 2 appels urgents',
        'icone':       '⚡',
        'couleur':     '#0ea5e9',
        'critere':     '2 réponses à des appels urgents',
        'niveau':      'silver',
    },
    {
        'code':        'fidele',
        'nom':         'Donneur Fidèle',
        'description': 'A donné deux années consécutives',
        'icone':       '📅',
        'couleur':     '#10b981',
        'critere':     'Dons sur 2 années consécutives',
        'niveau':      'gold',
    },
    {
        'code':        'sauveur_vies',
        'nom':         'Sauveur de Vies',
        'description': 'Potentiellement sauvé 10+ vies (≥ 4 dons × 3)',
        'icone':       '🏆',
        'couleur':     '#f59e0b',
        'critere':     '4 dons enregistrés (12+ vies potentielles)',
        'niveau':      'platinum',
    },
]

BADGE_MAP = {b['code']: b for b in BADGE_DEFINITIONS} #Pour accéder rapidement à un badge avec son code


def _check_premier_don(donneur):
    from .models import Don
    return Don.objects.filter(donneur=donneur).exists()


def _check_donneur_regulier(donneur):
    from .models import Don
    return Don.objects.filter(donneur=donneur).count() >= 3


def _check_heros_sang(donneur):
    from .models import Don
    return Don.objects.filter(donneur=donneur).count() >= 5


def _check_repondeur_urgent(donneur):
    from .models import ReponseAppel
    return ReponseAppel.objects.filter(donneur=donneur).count() >= 2


def _check_fidele(donneur):
    from .models import Don
    annees = Don.objects.filter(donneur=donneur)\
                        .values_list('date_don__year', flat=True)\
                        .distinct()
    annees = sorted(set(annees))
    if len(annees) < 2:
        return False
    for i in range(len(annees) - 1):
        if annees[i + 1] - annees[i] == 1:
            return True
    return False


def _check_sauveur_vies(donneur):
    from .models import Don
    return Don.objects.filter(donneur=donneur).count() >= 4


CHECKERS = {                #dictionnaire qui associe le code du badge a sa fct de verification 
    'premier_don':      _check_premier_don,
    'donneur_regulier': _check_donneur_regulier,
    'heros_sang':       _check_heros_sang,
    'repondeur_urgent': _check_repondeur_urgent,
    'fidele':           _check_fidele,
    'sauveur_vies':     _check_sauveur_vies,
}


def calculer_badges(donneur):
    """
    Retourne la liste des codes de badges obtenus par le donneur.
    Crée/met à jour les objets DonneurBadge en base.
    """
    from .models import DonneurBadge

    obtenus = []                #liste des badges gagnés
    for code, checker in CHECKERS.items():
        if checker(donneur):
            obtenus.append(code)
            # Créer l'entrée si elle n'existe pas encore
            DonneurBadge.objects.get_or_create(
                donneur=donneur,
                code=code,
                defaults={'date_obtention': timezone.now()}
            )

    return obtenus


def get_badges_donneur(donneur):
    """
    Retourne deux listes :
      - badges_obtenus  : dicts enrichis des badges déjà acquis
      - badges_a_venir  : dicts des badges pas encore obtenus
    """
    obtenus_codes = calculer_badges(donneur)

    from .models import DonneurBadge, Don, ReponseAppel

    total_dons    = Don.objects.filter(donneur=donneur).count()
    total_reponses = ReponseAppel.objects.filter(donneur=donneur).count()

    badges_obtenus = []
    badges_a_venir = []

    for b in BADGE_DEFINITIONS:
        code = b['code']
        info = dict(b)  # copie pour ne pas muter BADGE_DEFINITIONS

        if code in obtenus_codes:
            db_obj = DonneurBadge.objects.filter(donneur=donneur, code=code).first()
            info['date_obtention'] = db_obj.date_obtention if db_obj else None
            badges_obtenus.append(info)
        else:
            # Calcul progression
            if code == 'premier_don':
                info['progression'] = min(total_dons * 100, 100)
                info['prog_label']  = f"{total_dons}/1 don"
            elif code == 'donneur_regulier':
                info['progression'] = min(int(total_dons / 3 * 100), 99)
                info['prog_label']  = f"{total_dons}/3 dons"
            elif code == 'heros_sang':
                info['progression'] = min(int(total_dons / 5 * 100), 99)
                info['prog_label']  = f"{total_dons}/5 dons"
            elif code == 'repondeur_urgent':
                info['progression'] = min(int(total_reponses / 2 * 100), 99)
                info['prog_label']  = f"{total_reponses}/2 réponses"
            elif code == 'sauveur_vies':
                info['progression'] = min(int(total_dons / 4 * 100), 99)
                info['prog_label']  = f"{total_dons}/4 dons"
            else:
                info['progression'] = 0
                info['prog_label']  = 'Conditions spéciales'

            badges_a_venir.append(info)

    return badges_obtenus, badges_a_venir


def get_classement_ville(ville, limit=10):
    """
    Retourne le top N des donneurs de la même ville,
    triés par nombre total de dons (anonymisé : prénom + initiale).
    """
    from .models import Don
    from accounts.models import DonneurProfile
    from django.db.models import Count

    qs = DonneurProfile.objects.filter(
        ville__iexact=ville,
        actif=True,
    ).annotate(
        nb_dons=Count('dons')
    ).filter(nb_dons__gt=0).order_by('-nb_dons')[:limit]

    classement = []
    for i, d in enumerate(qs, start=1):
        prenom = d.user.first_name or d.user.username
        nom_masque = prenom[:1].upper() + '.' if len(prenom) > 1 else prenom
        classement.append({
            'rang':     i,
            'nom':      f"{prenom[0].upper()}{prenom[1:3].lower()}.",   # "Sa." par ex.
            'groupe':   d.groupe_sanguin,
            'nb_dons':  d.nb_dons,
            'vies':     d.nb_dons * 3,
        })
    return classement