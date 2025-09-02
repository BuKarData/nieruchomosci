from django.core.management.base import BaseCommand
from oferty.models import Oferta
import requests
import json
from datetime import date

class Command(BaseCommand):
    help = "Generuje dzienny raport ofert i wysyła go do API"

    def handle(self, *args, **kwargs):
        oferty = Oferta.objects.prefetch_related("ceny").all()

        # Przygotowanie danych do raportu
        raport = {
            "data": str(date.today()),
            "oferty": []
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None

            # Dodanie danych oferty do raportu
            raport["oferty"].append({
                "id": oferta.id,
                "adres": oferta.adres,
                "metraz": float(oferta.metraz) if oferta.metraz else None,
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,  # Decimal -> float
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            })

        # Wysyłka raportu do API / webhook
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"  # zamień na własny endpoint
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url_api, headers=headers, data=json.dumps(raport))
            self.stdout.write(self.style.SUCCESS(f"Raport wysłany, status: {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu: {e}"))
