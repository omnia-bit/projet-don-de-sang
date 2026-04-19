from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonneurProfile, HopitalProfile



# INSCRIPTION USER

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']



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