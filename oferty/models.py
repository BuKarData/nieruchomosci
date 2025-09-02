from django.db import models
from decimal import Decimal

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=200)
    adres = models.CharField(max_length=300)
    data_dodania = models.DateTimeField(auto_now_add=True)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)
    opis = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.nazwa


class Oferta(models.Model):
    STATUS_CHOICES = [
        ("dostępne", "Dostępne"),
        ("sprzedane", "Sprzedane"),
        ("rezerwacja", "Rezerwacja"),
    ]

    inwestycja = models.ForeignKey(
        "Inwestycja",
        related_name="oferty",
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
    )
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pokoje = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="dostępne")
    data_dodania = models.DateTimeField(auto_now_add=True)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)

    def __str__(self):
        return f"{self.adres} ({self.metraz} m², {self.pokoje} pok.)"


class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, related_name="ceny", on_delete=models.CASCADE)
    kwota = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()

    class Meta:
        ordering = ["data"]

    def __str__(self):
        return f"{self.kwota} zł ({self.data})"

class InwestycjaZdjecie(models.Model):
    inwestycja = models.ForeignKey(Inwestycja, related_name="zdjecia", on_delete=models.CASCADE)
    obraz = models.ImageField(upload_to="inwestycje/galeria/")

    def __str__(self):
        return f"Zdjęcie {self.id} - {self.inwestycja.nazwa}"