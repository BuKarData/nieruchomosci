from django import forms
from .models import Oferta, Cena

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        # Upewnij się, że wymieniasz tylko istniejące pola:
        fields = ['adres', 'metraz', 'status', 'zdjecie', 'opis', 'pokoje']  

class CenaForm(forms.ModelForm):
    class Meta:
        model = Cena
        fields = ['kwota', 'data']
