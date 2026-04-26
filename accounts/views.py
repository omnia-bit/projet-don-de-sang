from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Page accounts fonctionne")

def connexion(request):
    return render(request, 'accounts/login.html')
