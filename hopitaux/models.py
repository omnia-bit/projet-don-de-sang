from django.db import models
from django.conf import settings


class HopitalProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hopital_profile')
    nom_etablissement = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)
    specialite = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nom_etablissement

class DemandeSang(models.Model):
    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )

    hopital = models.ForeignKey(HopitalProfile, on_delete=models.CASCADE, related_name='demandes')
    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_CHOICES)
    quantite_necessaire = models.PositiveIntegerField(help_text="Nombre de poches ou volume")
    date_publication = models.DateTimeField(auto_now_add=True)
    est_resolue = models.BooleanField(default=False)
    description = models.TextField(blank=True, help_text="Raison de l'urgence")

    def __str__(self):
        status = "Résolue" if self.est_resolue else "En attente"
        return f"Demande {self.groupe_sanguin} par {self.hopital.nom_etablissement} ({status})"

class CampagneCollecte(models.Model):
    hopital = models.ForeignKey(HopitalProfile, on_delete=models.CASCADE, related_name='campagnes')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    lieu = models.CharField(max_length=200)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    
    def __cloturee__(self):
        from django.utils import timezone
        return timezone.now() > self.date_fin

    def __str__(self):
        return f"{self.titre} - {self.hopital.nom_etablissement}"
