from django.db import models

class Oferta(models.Model):
    STATUSY = [
        ("Dostępne", "Dostępne"),
        ("Sprzedane", "Sprzedane"),
        ("Rezerwacja", "Rezerwacja"),
    ]

    adres = models.CharField(max_length=255)
    metraz = models.FloatField()
    pokoje = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUSY, default="Dostępne")
    data_dodania = models.DateTimeField(auto_now_add=True)   
    
    def __str__(self):
        return f"{self.adres} - {self.status}"




class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, related_name='ceny', on_delete=models.CASCADE)
    kwota = models.CharField(max_length=50)  # np. "350 000 zł"
    data = models.DateField()

    class Meta:
        ordering = ['data']  # automatycznie sortuje ceny po dacie rosnąco

    def __str__(self):
        return f"{self.kwota} ({self.data})"
