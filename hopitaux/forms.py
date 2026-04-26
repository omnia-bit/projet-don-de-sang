from django import forms
from .models import DemandeSang, CampagneCollecte, StockSang

# Formulaire pour permettre aux hôpitaux de publier une demande de sang
class DemandeSangForm(forms.ModelForm):
    class Meta:
        model = DemandeSang
        # Nous excluons 'hopital', 'date_publication' et 'est_resolue' car ils seront gérés par la vue
        fields = ['groupe_sanguin', 'quantite_necessaire', 'description']
        
        # Personnalisation des widgets pour utiliser Bootstrap
        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'quantite_necessaire': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de poches'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': "Motif de l'urgence..."}),
        }

# Formulaire pour les campagnes de collecte
class CampagneCollecteForm(forms.ModelForm):
    class Meta:
        model = CampagneCollecte
        fields = ['titre', 'description', 'lieu', 'date_debut', 'date_fin']
        
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la campagne'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Détails de la campagne...'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de la collecte'}),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

# Formulaire pour la gestion de stock
class StockSangForm(forms.ModelForm):
    class Meta:
        model = StockSang
        fields = ['groupe_sanguin', 'quantite_poches']
        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'quantite_poches': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
