from django.core.management.base import BaseCommand
from datetime import date
import json
import requests
from oferty.models import Oferta  # <-- poprawny import

class Command(BaseCommand):
    help = "Wysyła raport ofert do API/webhooku"

    def handle(self, *args, **options):
        oferty = Oferta.objects.prefetch_related("ceny").all()

        raport = {
            "data": str(date.today()),
            "oferty": []
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None

            raport["oferty"].append({
                "id": oferta.id,
                "adres": oferta.adres,
                "metraz": oferta.metraz,
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            })

        # Wysyłka raportu
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url_api, headers=headers, data=json.dumps(raport))
            self.stdout.write(self.style.SUCCESS(f"Raport wysłany, status: {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu: {e}"))
