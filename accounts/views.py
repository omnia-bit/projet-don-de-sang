from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm


# HOME = LOGIN PAGE
def home(request):
    return render(request, 'registration/login.html')


# REGISTER
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
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

            # 🔥 REDIRECTION PAR ROLE
            if user.role == 'donneur':
                return redirect('dashboard_donneur')

            elif user.role == 'hopital':
                return redirect('dashboard_hopital')

            elif user.role == 'admin':
                return redirect('dashboard_admin')

            return redirect('home')

    return render(request, 'registration/login.html')


# DASHBOARDS
@login_required
def dashboard_donneur(request):
    return render(request, 'donneurs/dashboard.html')


@login_required
def dashboard_hopital(request):
    return render(request, 'hopitaux/dashboard.html')


@login_required
def dashboard_admin(request):
    return render(request, 'administration/dashboard.html')