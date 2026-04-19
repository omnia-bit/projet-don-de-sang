from django.db import models
from django.contrib.auth.models import AbstractUser

# USER PERSONNALISÉ

class User(AbstractUser):
    ROLE_CHOICES = (
        ('donneur', 'Donneur'),
        ('hopital', 'Hôpital'),
        ('admin', 'Administrateur'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def is_donneur(self):
        return self.role == 'donneur'

    def is_hopital(self):
        return self.role == 'hopital'

# PROFIL DONNEUR
class DonneurProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donneur_profile')

    groupe_sanguin = models.CharField(max_length=5)
    sexe = models.CharField(max_length=10)
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.groupe_sanguin})"

# PROFIL HÔPITAL

class HopitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hopital_profile')

    nom = models.CharField(max_length=200)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=100)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return self.nom