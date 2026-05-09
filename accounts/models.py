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



import uuid

# PROFIL DONNEUR

class DonneurProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donneur_profile'
    )

    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )

    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_CHOICES, null=True, blank=True)
    sexe = models.CharField(max_length=10, null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    actif = models.BooleanField(default=True)
    
    # Identifiant pour QR Code
    qr_code_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.groupe_sanguin})"


# PROFIL HÔPITAL

class HopitalProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hopital_profile'
    )

    nom = models.CharField(max_length=200)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=100)
    valide = models.BooleanField(default=False)
    
    # Nouveaux champs pour la vérification moderne
    licence_doc = models.FileField(upload_to='licences/', null=True, blank=True)

    def __str__(self):
        return self.nom