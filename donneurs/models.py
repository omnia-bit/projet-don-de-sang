from django.db import models
from django.conf import settings

class DonneurProfile(models.Model):
    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donneur_profile')
    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_CHOICES)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=15)
    adresse = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.groupe_sanguin}"

class Don(models.Model):
    donneur = models.ForeignKey(DonneurProfile, on_delete=models.CASCADE, related_name='dons')
    date_don = models.DateField(auto_now_add=True)
    lieu = models.CharField(max_length=200) # Nom de l'hôpital ou du centre
    quantite = models.PositiveIntegerField(help_text="Quantité en ml")
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Don de {self.donneur.user.username} le {self.date_don}"
