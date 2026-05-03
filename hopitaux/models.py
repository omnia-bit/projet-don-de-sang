from django.db import models
from accounts.models import HopitalProfile
# DEMANDE DE SANG 
class DemandeSang(models.Model):
    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )

    STATUT_CHOICES = (
        ('active', 'Active'),
        ('cloturee', 'Clôturée'),
    )

    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.CASCADE,
        related_name='demandes'
    )

    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_CHOICES)
    quantite_necessaire = models.PositiveIntegerField(verbose_name="Nombre de poches")
    delai = models.PositiveIntegerField(verbose_name="Délai (heures)", default=24)
    description = models.TextField(blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')

    def __str__(self):
        return f"{self.groupe_sanguin} - {self.hopital.nom} ({self.statut})"
# CAMPAGNE DE DON 
class CampagneCollecte(models.Model):
    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.CASCADE,
        related_name='campagnes'
    )

    titre = models.CharField(max_length=200)
    description = models.TextField()
    lieu = models.CharField(max_length=200)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    groupes_cibles = models.CharField(max_length=200, help_text="Ex: A+, O-, Tous", default="Tous")
    capacite_totale = models.PositiveIntegerField(default=50)
    nb_creneaux = models.PositiveIntegerField(default=5, verbose_name="Nombre de créneaux horaires")

    def __str__(self):
        return f"{self.titre} - {self.hopital.nom}"
# STOCK DE SANG PAR HÔPITAL
class StockSang(models.Model):
    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )

    hopital = models.ForeignKey(
        HopitalProfile,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_CHOICES)
    quantite_poches = models.PositiveIntegerField(default=0)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hopital', 'groupe_sanguin')

    def __str__(self):
        return f"{self.hopital.nom} - {self.groupe_sanguin} : {self.quantite_poches} poches"
