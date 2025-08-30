import json
import requests
from datetime import date
from django.core.management.base import BaseCommand
from oferty.models import Oferta

class Command(BaseCommand):
    help = "Wysyła dzienny raport ofert do webhooka"

    def handle(self, *args, **options):
        oferty = Oferta.objects.prefetch_related("ceny").all()

        raport = {
            "data": str(date.today()),
            "oferty": []
        }

        for oferta in oferty:
            ceny = list(oferta.ceny.all().order_by('data'))
            ostatnia_cena = ceny[-1] if ceny else None
            raport["oferty"].append({
                "id": oferta.id,
                "adres": oferta.adres,
                "metraz": oferta.metraz,
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            })

        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url_api, headers=headers, data=json.dumps(raport))
            self.stdout.write(self.style.SUCCESS(f"Raport wysłany, status: {response.status_code}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Błąd wysyłki raportu: {e}"))
