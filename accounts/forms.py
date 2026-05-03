from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonneurProfile, HopitalProfile



# INSCRIPTION USER
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    
    # Champs additionnels pour le donneur (seront affichés via JS)
    groupe_sanguin = forms.ChoiceField(
        choices=[('', 'Choisir votre groupe')] + list(DonneurProfile.GROUPE_CHOICES), 
        required=False
    )
    ville = forms.CharField(max_length=100, required=False)
    sexe = forms.ChoiceField(
        choices=[('', 'Sexe'), ('M', 'Homme'), ('F', 'Femme')], 
        required=False
    )

    # Champs additionnels pour l'hôpital
    nom_hopital = forms.CharField(max_length=200, required=False, label="Nom de l'hôpital")
    adresse_hopital = forms.CharField(max_length=500, required=False, label="Adresse complète")
    agrement = forms.CharField(max_length=100, required=False, label="Numéro d'agrément")

    class Meta:
        model = User
        fields = ['username', 'email', 'role']
# PROFIL DONNEUR

class DonneurProfileForm(forms.ModelForm):
    class Meta:
        model = DonneurProfile
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville', 'actif']


# PROFIL HÔPITAL

class HopitalProfileForm(forms.ModelForm):
    class Meta:
        model = HopitalProfile
        fields = ['nom', 'adresse', 'ville', 'agrement', 'valide']
        
class ModifierProfilForm(forms.ModelForm):
    class Meta:
        model = DonneurProfile
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']

        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'sexe': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
        }