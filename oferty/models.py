from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ('dostępne', 'Dostępne'),
    ('sprzedane', 'Sprzedane'),
    ('rezerwacja', 'Rezerwacja'),
]

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=200)
    opis = models.TextField(blank=True)
    zdjecie = models.ImageField(upload_to='inwestycje/', blank=True, null=True)

    def __str__(self):
        return self.nazwa

class Oferta(models.Model):
    inwestycja = models.ForeignKey(Inwestycja, on_delete=models.CASCADE, related_name='oferty')
    adres = models.CharField(max_length=200)
    metraz = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pokoje = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='dostępne')
    
    # Poprawione pole data_dodania
    data_dodania = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.inwestycja.nazwa} - {self.adres}"

class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='ceny')
    kwota = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.kwota} zł - {self.data}"
