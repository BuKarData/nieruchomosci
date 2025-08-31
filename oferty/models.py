from django.db import models

# -------- Inwestycja --------
class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=255)
    opis = models.TextField(blank=True, null=True)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)

    def __str__(self):
        return self.nazwa


# -------- Oferta (lokal) --------
STATUS_CHOICES = [
    ("wolny", "Wolny"),
    ("rezerwacja", "Rezerwacja"),
    ("sprzedany", "Sprzedany"),
]

class Oferta(models.Model):
    inwestycja = models.ForeignKey(
        Inwestycja,
        on_delete=models.CASCADE,
        related_name="oferty"
    )
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2)
    cena = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="wolny")
    pokoje = models.IntegerField(default=1)  # liczba pokoi

    def __str__(self):
        return f"{self.inwestycja.nazwa} - {self.adres}"
