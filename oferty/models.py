from django.db import models

# --- Model inwestycji ---
class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=255)
    opis = models.TextField(blank=True, null=True)
    zdjecie = models.ImageField(upload_to='inwestycje/', blank=True, null=True)
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nazwa

# --- Model oferty / lokalu ---
STATUS_CHOICES = [
    ('dostępne', 'Dostępne'),
    ('sprzedane', 'Sprzedane'),
    ('rezerwacja', 'Rezerwacja'),
]

class Oferta(models.Model):
    inwestycja = models.ForeignKey(Inwestycja, on_delete=models.CASCADE, related_name='oferty')
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pokoje = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='dostępne')
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inwestycja.nazwa} - {self.adres}"

    @property
    def ostatnia_cena(self):
        return self.ceny.order_by('-data').first()

    @property
    def ceny_list(self):
        return self.ceny.order_by('data')

    @property
    def cena_m2(self):
        if self.ostatnia_cena and self.metraz:
            return self.ostatnia_cena.kwota / float(self.metraz)
        return None

    @property
    def chart_data(self):
        labels = [c.data.strftime('%Y-%m-%d') for c in self.ceny_list]
        data = [c.kwota for c in self.ceny_list]
        return {'labels': labels, 'data': data}

# --- Model historii cen ---
class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='ceny')
    kwota = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.kwota} zł ({self.data})"
