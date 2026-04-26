from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard'),
    path('validation/', views.valider_hopitaux, name='validation_hopitaux'),
    path('validation/<int:pk>/<str:action>/', views.action_validation_hopital, name='action_validation'),
]