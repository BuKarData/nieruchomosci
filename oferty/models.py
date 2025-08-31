from django.db import models
from decimal import Decimal


class Oferta(models.Model):
    STATUS_CHOICES = [
        ("dostępne", "Dostępne"),
        ("sprzedane", "Sprzedane"),
        ("rezerwacja", "Rezerwacja"),
    ]

    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # np. 123.45 m2
    pokoje = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="dostępne")
    data_dodania = models.DateTimeField(auto_now_add=True)  # data utworzenia rekordu
    zdjecie = models.ImageField(upload_to='inwestycje/', blank=True, null=True)
    def __str__(self):
        return f"{self.adres} ({self.metraz} m², {self.pokoje} pok.)"


class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, related_name="ceny", on_delete=models.CASCADE)
    kwota = models.DecimalField(max_digits=12, decimal_places=2)

  # np. 450000.00
    data = models.DateField()

    class Meta:
        ordering = ["data"]  # zawsze sortuj ceny rosnąco po dacie

    def __str__(self):
        return f"{self.kwota} zł ({self.data})"