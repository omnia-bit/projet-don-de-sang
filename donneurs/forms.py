from django import forms
from django.utils import timezone
from .models import Don, ReponseAppel

# Import sécurisé de HopitalProfile
try:
    from accounts.models import HopitalProfile
    HOPITAL_QUERYSET = HopitalProfile.objects.filter(valide=True)
except Exception:
    HOPITAL_QUERYSET = None


class DonForm(forms.ModelForm):

    # Champ hopital optionnel
    if HOPITAL_QUERYSET is not None:
        hopital = forms.ModelChoiceField(
            queryset=HOPITAL_QUERYSET,
            required=False,
            empty_label="— Sélectionner un hôpital (optionnel) —",
            widget=forms.Select(attrs={'class': 'form-select'})
        )

    class Meta:
        model  = Don
        fields = ['date_don', 'hopital', 'quantite', 'lieu', 'observations']
        widgets = {
            'date_don': forms.DateInput(attrs={
                'class': 'form-control',
                'type':  'date',
                'max':   timezone.now().date().isoformat(),   # pas de date future
            }),
            'quantite': forms.NumberInput(attrs={
                'class':       'form-control',
                'placeholder': 'Ex: 450',
                'min':         1,
                'max':         600,
            }),
            'lieu': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Ex: Hôpital Charles Nicolle, Tunis',
            }),
            'observations': forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Remarques éventuelles...',
                'rows':        3,
            }),
        }
        labels = {
            'date_don':     'Date du don',
            'quantite':     'Quantité donnée (ml)',
            'lieu':         'Lieu du don',
            'observations': 'Observations',
        }


class ReponseAppelForm(forms.ModelForm):
    """
    Le formulaire ne contient qu'un message libre optionnel.
    donneur et demande_id sont injectés dans la vue.
    """
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class':       'form-control',
            'rows':        3,
            'placeholder': "Message optionnel à l'hôpital...",
        }),
        label="Message (optionnel)"
    )

    class Meta:
        model  = ReponseAppel
        fields = []   # tous les champs métier sont injectés dans la vue