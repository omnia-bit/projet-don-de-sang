from django.db import models
from accounts.models import DonneurProfile, HopitalProfile

class Don(models.Model):
    donneur = models.ForeignKey(
        DonneurProfile,
        on_delete=models.CASCADE,
        related_name='dons'
    )
    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dons_recus'
    )
    date_don     = models.DateField()
    quantite     = models.PositiveIntegerField(help_text="Quantité en ml (ex: 450)")
    lieu         = models.CharField(max_length=200)
    observations = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_don']
        verbose_name = "Don"
        verbose_name_plural = "Dons"

    def __str__(self):
        return f"Don de {self.donneur.user.username} — {self.date_don}"
class ReponseAppel(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme',   'Confirmé'),
        ('annule',     'Annulé'),
    ]

    donneur = models.ForeignKey(
        DonneurProfile,
        on_delete=models.CASCADE,
        related_name='reponses_appels'
    )
    demande = models.ForeignKey(
        'hopitaux.DemandeSang',
        on_delete=models.CASCADE,
        related_name='reponses',
        null=True 
    )
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut       = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )

    class Meta:
        ordering = ['-date_reponse']
        verbose_name = "Réponse à un appel"
        verbose_name_plural = "Réponses aux appels"
        unique_together = [('donneur', 'demande')]

    def __str__(self):
        return f"Réponse de {self.donneur.user.username} — demande #{self.demande.id}"
class InscriptionCampagne(models.Model):
    donneur = models.ForeignKey(
        DonneurProfile,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    campagne = models.ForeignKey(
        'hopitaux.CampagneCollecte',
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    creneau_horaire = models.CharField(max_length=100, help_text="Ex: 09:00 - 10:00")
    date_inscription = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inscription à une campagne"
        unique_together = [('donneur', 'campagne')]

    def __str__(self):
        return f"{self.donneur.user.username} - {self.campagne.titre} ({self.creneau_horaire})"
