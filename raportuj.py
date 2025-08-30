# raportuj.py

from datetime import date
import json
import requests
from django.core.management.base import BaseCommand
from oferty.models import Oferta

class Command(BaseCommand):
    help = 'Generuje codzienny raport ofert i wysyła do webhooka'

    def handle(self, *args, **options):
        oferty = Oferta.objects.prefetch_related("ceny").all()

        raport = {
            "data": str(date.today()),
            "oferty": []
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            if ceny_list:
                ostatnia_cena_obj = ceny_list[-1]
                try:
                    ostatnia_kwota = float(str(ostatnia_cena_obj.kwota).replace(" ", "").replace("zł", ""))
                except (ValueError, TypeError):
                    ostatnia_kwota = None
            else:
                ostatnia_kwota = None
                ostatnia_cena_obj = None

            raport["oferty"].append({
                "id": oferta.id,
                "adres": oferta.adres,
                "metraz": oferta.metraz,
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": float(ostatnia_kwota) if ostatnia_kwota is not None else None,
                "data_ceny": ostatnia_cena_obj.data.isoformat() if ostatnia_cena_obj else None
            })

        # Wysyłka raportu do webhooka
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"  # zamień na prawdziwe API jeśli trzeba
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url_api, headers=headers, data=json.dumps(raport))
            self.stdout.write(self.style.SUCCESS(f"Raport wysłany, status: {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu: {e}"))
