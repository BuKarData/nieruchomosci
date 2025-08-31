# oferty/forms.py
from django import forms
from .models import Inwestycja, Oferta


class InwestycjaForm(forms.ModelForm):
    class Meta:
        model = Inwestycja
        fields = ["nazwa", "opis", "zdjecie"]


class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ["inwestycja", "adres", "metraz", "cena", "status", "pokoje", "zdjecie"]
