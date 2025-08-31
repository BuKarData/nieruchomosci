from django.db import models
from decimal import Decimal

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=255)
    opis = models.TextField(blank=True, null=True)
    zdjecie = models.ImageField(upload_to='inwestycje/', blank=True, null=True)

    def __str__(self):
        return self.nazwa

STATUS_CHOICES = [
    ('dostepne', 'Dostępne'),
    ('rezerwacja', 'Rezerwacja'),
    ('sprzedane', 'Sprzedane'),
]
class Oferta(models.Model):
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    zdjecie = models.ImageField(upload_to='inwestycje/', null=True, blank=True)
    pokoje = models.IntegerField(null=True, blank=True)
    opis = models.TextField(blank=True, null=True)
   def __str__(self):
        return self.adres


class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, related_name="ceny", on_delete=models.CASCADE)
    kwota = models.DecimalField(max_digits=12, decimal_places=2)

  # np. 450000.00
    data = models.DateField()

    class Meta:
        ordering = ["data"]  # zawsze sortuj ceny rosnąco po dacie

    def __str__(self):
        return f"{self.kwota} zł ({self.data})"
