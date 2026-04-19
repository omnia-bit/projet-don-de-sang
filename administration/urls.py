from django.urls import path
from . import views

urlpatterns = [
    # exemple
    path('', views.index, name='administration_home'),
]