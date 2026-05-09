from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.http import HttpResponse
from .models import DonneurProfile, HopitalProfile
from .forms import ModifierProfilForm

def index(request):
    return HttpResponse("Page accounts fonctionne")


# HOME = LOGIN PAGE
def home(request):
    return render(request, 'registration/login.html')


# REGISTER
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            role = form.cleaned_data.get('role')

            if role == 'donneur':
                DonneurProfile.objects.create(
                    user=user,
                    groupe_sanguin=form.cleaned_data.get('groupe_sanguin') or 'O+',
                    sexe=form.cleaned_data.get('sexe') or 'M',
                    date_naissance='2000-01-01',
                    ville=form.cleaned_data.get('ville') or 'Non définie'
                )

            elif role == 'hopital':
                HopitalProfile.objects.create(
                    user=user,
                    nom=form.cleaned_data.get('nom_hopital') or user.username,
                    adresse=form.cleaned_data.get('adresse_hopital') or "Non définie",
                    ville=form.cleaned_data.get('ville_hopital') or "Non définie",
                    agrement=form.cleaned_data.get('agrement') or "N/A",
                    licence_doc=form.cleaned_data.get('licence_doc')
                )

            return redirect('accounts:login')  

    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


from django.views.decorators.csrf import csrf_exempt

# LOGIN CUSTOM
@csrf_exempt
def custom_login(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url == 'None':
        next_url = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Si un paramètre 'next' existe et est valide, on redirige vers celui-ci
            if next_url and next_url != 'None':
                return redirect(next_url)

            # Sinon redirection par défaut selon le rôle
            if user.role == 'admin':
                return redirect('administration:dashboard')
            elif user.role == 'donneur':
                return redirect('donneurs:dashboard')
            elif user.role == 'hopital':
                return redirect('hopitaux:dashboard')
            else:
                return redirect('accueil') # Fallback

        return render(request, 'registration/login.html', {
            'error': 'Nom utilisateur ou mot de passe incorrect',
            'next': next_url
        })

    return render(request, 'registration/login.html', {'next': next_url})


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# DASHBOARDS REDIRECTS (pour assurer la cohérence)
@login_required
def dashboard_donneur(request):
    return redirect('donneurs:dashboard')


@login_required
def dashboard_hopital(request):
    return redirect('hopitaux:dashboard')


@login_required
def dashboard_admin(request):
    return redirect('administration:dashboard')


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