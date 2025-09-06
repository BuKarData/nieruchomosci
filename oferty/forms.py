from django import forms
from .models import Oferta, Cena
from .models import Nieruchomosc

class NieruchomoscForm(forms.ModelForm):
    class Meta:
        model = Nieruchomosc
        fields = ['nazwa', 'opis', 'cena', 'metraz', 'pokoje', 'status', 'zdjecie']
        widgets = {
            'status': forms.Select(choices=Nieruchomosc.STATUS_CHOICES),
        }
class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ['adres', 'metraz', 'pokoje', 'status']  


class CenaForm(forms.ModelForm):
    class Meta:
        model = Cena
        fields = ['oferta', 'kwota', 'data']