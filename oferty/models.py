from django.db import models
from decimal import Decimal

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=255)
    opis = models.TextField(blank=True, null=True)
    zdjecie = models.ImageField(upload_to='inwestycje/', blank=True, null=True)

    def __str__(self):
        return self.nazwa

class Oferta(models.Model):
    inwestycja = models.ForeignKey(Inwestycja, related_name='oferty', on_delete=models.CASCADE)
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('dostępne','Dostępne'), ('rezerwacja','Rezerwacja'), ('sprzedane','Sprzedane')])
    kwota = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    zdjecie = models.ImageField(upload_to='oferty/', blank=True, null=True)
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
