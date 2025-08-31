from django.db import models
from django.utils import timezone

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=255)
    adres = models.CharField(max_length=255)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nazwa


class Oferta(models.Model):
    STATUS_CHOICES = [
        ("dostepne", "Dostępne"),
        ("sprzedane", "Sprzedane"),
        ("rezerwacja", "Rezerwacja"),
    ]

    inwestycja = models.ForeignKey(Inwestycja, on_delete=models.CASCADE, related_name="oferty")
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pokoje = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="dostepne")
    ostatnia_cena = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adres} ({self.inwestycja.nazwa})"

    @property
    def cena_m2(self):
        if self.ostatnia_cena and self.metraz:
            return self.ostatnia_cena / self.metraz
        return None
