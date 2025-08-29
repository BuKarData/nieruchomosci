from django import forms
from .models import Oferta, Cena

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ['nazwa', 'status', 'metraz']

class CenaForm(forms.ModelForm):
    class Meta:
        model = Cena
        fields = ['oferta', 'kwota', 'data']
