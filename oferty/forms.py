from django import forms
from .models import Inwestycja, Oferta

# -------- Formularz dla inwestycji --------
class InwestycjaForm(forms.ModelForm):
    class Meta:
        model = Inwestycja
        fields = ["nazwa", "opis", "zdjecie"]


# -------- Formularz dla oferty/lokalu --------
class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ["inwestycja", "adres", "metraz", "cena", "status", "pokoje"]
