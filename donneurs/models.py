from django.db import models
from accounts.models import DonneurProfile, HopitalProfile

# HISTORIQUE DES DONS

class Don(models.Model):
    donneur = models.ForeignKey(
        DonneurProfile,
        on_delete=models.CASCADE,
        related_name='dons'
    )

    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    date_don = models.DateField(auto_now_add=True)
    quantite = models.PositiveIntegerField(help_text="Quantité en ml")
    lieu = models.CharField(max_length=200)
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Don de {self.donneur.user.username} - {self.date_don}"



# RÉPONSE AUX APPELS URGENTS

class ReponseAppel(models.Model):
    donneur = models.ForeignKey(DonneurProfile, on_delete=models.CASCADE)
    demande_id = models.IntegerField()  # (sera lié à hopitaux.DemandeSang)
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="en attente")

    def __str__(self):
        return f"Réponse de {self.donneur.user.username}"