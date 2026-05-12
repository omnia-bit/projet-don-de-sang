from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User, DonneurProfile, HopitalProfile
from hopitaux.models import DemandeSang, CampagneCollecte, StockSang
from donneurs.models import Don
from django.db.models import Sum, Q, Count

import csv
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    import json
    from datetime import timedelta
    from django.utils import timezone
    
    # Les chiffres du site
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
    
    # Graphique par groupe
    groupes = ['O-', 'A-', 'B+', 'O+', 'A+', 'B-', 'AB+', 'AB-']
    demandes_par_groupe_qs = DemandeSang.objects.filter(statut='active').values('groupe_sanguin').annotate(total=Sum('quantite_necessaire'))
    demandes_dict = {d['groupe_sanguin']: d['total'] or 0 for d in demandes_par_groupe_qs}
    
    labels_stock = groupes
    data_stock = [demandes_dict.get(g, 0) for g in groupes]

    # Alertes manque de sang
    stock_actuel = StockSang.objects.values('groupe_sanguin').annotate(total=Sum('quantite_poches'))
    alertes_penurie = [s for s in stock_actuel if s['total'] < 20]

    # Villes avec le plus de demandes
    demandes_par_ville = DemandeSang.objects.filter(statut='active')\
        .exclude(hopital__ville__isnull=True)\
        .exclude(hopital__ville__exact='')\
        .values('hopital__ville')\
        .annotate(total=Count('id'))\
        .order_by('-total')

    # Courbe des dons sur 1 mois
    today = timezone.now().date()
    date_debut_30j = today - timedelta(days=29)
    dons_par_jour = Don.objects.filter(date_don__gte=date_debut_30j).values('date_don').annotate(total=Count('id')).order_by('date_don')
    
    dons_dict = {d['date_don']: d['total'] for d in dons_par_jour}
    line_labels = []
    line_data = []
    for i in range(30):
        jour = date_debut_30j + timedelta(days=i)
        line_labels.append(jour.strftime('%d %b'))
        line_data.append(dons_dict.get(jour, 0))

    # Petites courbes de tendance
    def get_sparkline_data(queryset, date_field):
        data = []
        for i in range(5):
            d_start = today - timedelta(days=(5-i)*7)
            d_end = today - timedelta(days=(4-i)*7)
            filter_kwargs = {f"{date_field}__range": [d_start, d_end]}
            data.append(queryset.filter(**filter_kwargs).count())
        return data

    spark_donneurs = get_sparkline_data(User.objects.filter(role='donneur'), 'date_joined')
    spark_hopitaux = get_sparkline_data(User.objects.filter(role='hopital'), 'date_joined')
    spark_demandes = get_sparkline_data(DemandeSang.objects.all(), 'date_publication')
    spark_dons = get_sparkline_data(Don.objects.all(), 'date_don')

    # Activités récentes
    dernieres_demandes = DemandeSang.objects.all().select_related('hopital').order_by('-date_publication')[:5]
    dernieres_campagnes = CampagneCollecte.objects.all().select_related('hopital').order_by('-date_debut')[:5]

    context = {
        'stats': stats,
        'labels_stock_json': json.dumps(labels_stock),
        'data_stock_json': json.dumps(data_stock),
        'line_labels_json': json.dumps(line_labels),
        'line_data_json': json.dumps(line_data),
        'spark_donneurs': json.dumps(spark_donneurs),
        'spark_hopitaux': json.dumps(spark_hopitaux),
        'spark_demandes': json.dumps(spark_demandes),
        'spark_dons': json.dumps(spark_dons),
        'alertes_penurie': alertes_penurie,
        'demandes_par_ville': demandes_par_ville,
        'dernieres_demandes': dernieres_demandes,
        'dernieres_campagnes': dernieres_campagnes,
        'titre_page': "Tableau de Bord National",
        'today': timezone.now(),
    }
    return render(request, 'administration/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def valider_hopitaux(request):
    query = request.GET.get('q')
    hopitaux_en_attente = HopitalProfile.objects.filter(valide=False)
    hopitaux_valides = HopitalProfile.objects.filter(valide=True)
    
    if query:
        hopitaux_en_attente = hopitaux_en_attente.filter(
            Q(nom__icontains=query) | Q(ville__icontains=query) | Q(agrement__icontains=query)
        )
        hopitaux_valides = hopitaux_valides.filter(
            Q(nom__icontains=query) | Q(ville__icontains=query) | Q(agrement__icontains=query)
        )

    context = {
        'en_attente': hopitaux_en_attente,
        'valides': hopitaux_valides,
        'titre_page': "Validation des Comptes Hospitaliers",
        'query': query
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
    # ... (code existing)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donneurs_bloodconnect.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nom d\'utilisateur', 'Email', 'Groupe Sanguin', 'Ville', 'Date d\'inscription'])

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

@login_required
@user_passes_test(is_admin)
def liste_demandes_urgentes(request):
    demandes = DemandeSang.objects.all().select_related('hopital').order_by('-date_publication')
    query = request.GET.get('q')
    if query:
        demandes = demandes.filter(
            Q(hopital__nom__icontains=query) | Q(groupe_sanguin__icontains=query) | Q(hopital__ville__icontains=query)
        )
    
    return render(request, 'administration/liste_demandes.html', {
        'demandes': demandes,
        'titre_page': "Toutes les Demandes Urgentes",
        'query': query
    })
