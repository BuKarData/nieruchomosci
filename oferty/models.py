# oferty/models.py
from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ("dostepne", "Dostępne"),
    ("rezerwacja", "Rezerwacja"),
    ("sprzedane", "Sprzedane"),
]


class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=100)
    data_dodania = models.DateTimeField(default=timezone.now)



    class Meta:
        verbose_name = "Inwestycja"
        verbose_name_plural = "Inwestycje"

    def __str__(self):
        return self.nazwa


class Oferta(models.Model):
    inwestycja = models.ForeignKey(
        Inwestycja, on_delete=models.CASCADE, related_name="oferty"
    )
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cena = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="dostepne")
    pokoje = models.IntegerField(null=True, blank=True)
    zdjecie = models.ImageField(upload_to="oferty/", blank=True, null=True)
    data_dodania = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Oferty"

    def __str__(self):
        return f"{self.inwestycja.nazwa} — {self.adres}"

    
