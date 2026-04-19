from django import forms
from .models import DemandeSang

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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motif de l'urgence...'}),
        }
