from django.db import models
from accounts.models import DonneurProfile, HopitalProfile


# ─────────────────────────────────────────────
# HISTORIQUE DES DONS
# ─────────────────────────────────────────────
class Don(models.Model):
    donneur = models.ForeignKey(
        DonneurProfile,
        on_delete=models.CASCADE,
        related_name='dons'
    )
    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.SET_NULL,   # SET_NULL : si l'hôpital est supprimé, le don reste
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


# ─────────────────────────────────────────────
# RÉPONSE AUX APPELS URGENTS
# ─────────────────────────────────────────────
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
    # Clé vers hopitaux.DemandeUrgente stockée en entier
    # (évite une dépendance circulaire entre les apps)
    demande_id   = models.IntegerField(verbose_name="ID de la demande urgente")
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
        # Un donneur ne peut répondre qu'une seule fois par demande
        unique_together = [('donneur', 'demande_id')]

    def __str__(self):
        return f"Réponse de {self.donneur.user.username} — demande #{self.demande_id}"