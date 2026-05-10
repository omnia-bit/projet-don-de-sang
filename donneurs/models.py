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
    signature_donneur = models.TextField(blank=True, null=True, help_text="Signature Base64 du donneur lors du don")

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

class ConversationChatbot(models.Model):
    donneur    = models.ForeignKey(DonneurProfile, on_delete=models.CASCADE, related_name='conversations')
    date_debut = models.DateTimeField(auto_now_add=True)
    titre      = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Conversation chatbot"

    def __str__(self):
        return f"Conversation de {self.donneur.user.username} — {self.date_debut.strftime('%d/%m/%Y %H:%M')}"


class MessageChatbot(models.Model):
    ROLE_CHOICES = [('user', 'Utilisateur'), ('assistant', 'Assistant')]
    conversation = models.ForeignKey(ConversationChatbot, on_delete=models.CASCADE, related_name='messages')
    role         = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenu      = models.TextField()
    date_envoi   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_envoi']

    def __str__(self):
        return f"{self.role} — {self.date_envoi.strftime('%H:%M')}"


class DonneurBadge(models.Model):
    CODES = [
        ('premier_don',      'Premier Pas'),
        ('donneur_regulier', 'Donneur Régulier'),
        ('heros_sang',       'Héros du Sang'),
        ('repondeur_urgent', 'Répondeur Urgent'),
        ('fidele',           'Donneur Fidèle'),
        ('sauveur_vies',     'Sauveur de Vies'),
    ]

    donneur         = models.ForeignKey(
        'accounts.DonneurProfile',
        on_delete=models.CASCADE,
        related_name='badges'
    )
    code            = models.CharField(max_length=50, choices=CODES)
    date_obtention  = models.DateTimeField()

    class Meta:
        unique_together = [('donneur', 'code')]
        ordering        = ['date_obtention']
        verbose_name    = "Badge donneur"

    def __str__(self):
        return f"{self.donneur.user.username} — {self.code}"

