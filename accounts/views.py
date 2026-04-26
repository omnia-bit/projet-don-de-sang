from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.http import HttpResponse
from .models import DonneurProfile, HopitalProfile
from .forms import ModifierProfilForm

def index(request):
    return HttpResponse("Page accounts fonctionne")

#def connexion(request):
    #return render(request, 'registration/login.html')


# HOME = LOGIN PAGE
def home(request):
    return render(request, 'registration/login.html')


# REGISTER
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = form.cleaned_data.get('role')

            #  création selon rôle
            if role == 'donneur':
                DonneurProfile.objects.create(
                    user=user,
                    groupe_sanguin='O+',      # valeur par défaut
                    sexe='Homme',             # ou 'Femme'
                    date_naissance='2000-01-01',
                    ville='Non définie'
                )

            elif role == 'hopital':
                HopitalProfile.objects.create(
                    user=user,
                    nom="Hôpital",
                    adresse="Non définie",
                    ville="Non définie",
                    agrement="N/A"
                )

            return redirect('login')

    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# LOGIN CUSTOM
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ADMIN
            if user.role == 'admin':
                return redirect('accounts:dashboard_admin')

            # DONNEUR
            if user.role == 'donneur':
                return redirect('accounts:dashboard_donneur')

            # HOPITAL
            if user.role == 'hopital':
                return redirect('accounts:dashboard_hopital')

            # fallback
            return redirect('accounts:login')

    return render(request, 'registration/login.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

# DASHBOARDS
@login_required
def dashboard_donneur(request):
    donneur, created = DonneurProfile.objects.get_or_create(user=request.user)

    return render(request, 'donneurs/dashboard.html', {
        'donneur': donneur,
        'est_eligible': True,
        'total_dons': 0,
        'dons_recents': [],
        'appels_compatibles': [],
        'prochaine_date': None,
        'jours_restants': 0,
        'progression': 0,
    })


@login_required
def dashboard_hopital(request):
    return render(request, 'hopitaux/dashboard.html')


@login_required
def dashboard_admin(request):
    return render(request, 'administration/dashboard.html')

@login_required
def modifier_profil(request):
    return render(request, 'accounts/modifier_profil.html')

@login_required
def modifier_profil(request):
    donneur = DonneurProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ModifierProfilForm(request.POST, instance=donneur)
        if form.is_valid():
            form.save()
            return redirect('accounts:dashboard_donneur')
    else:
        form = ModifierProfilForm(instance=donneur)

    return render(request, 'registration/modifier_profil.html', {
        'form': form,
        'donneur': donneur
    })