from django.core.management.base import BaseCommand
from oferty.models import Oferta
from datetime import datetime
import requests
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Generuje dzienny raport ofert zgodny z art. 19b ustawy i wysyła go do API ministerstwa"

    def handle(self, *args, **kwargs):
        oferty = Oferta.objects.prefetch_related("ceny", "pomieszczenia", "swiadczenia").all()

        raport = {
            "meta": {
                "wersja": "1.0",
                "data_raportu": datetime.now().isoformat(),
                "źródło": "BuKarData",
                "typ_danych": "oferty_mieszkaniowe"
            },
            "oferty": []
        }

        for oferta in oferty:
            ceny = list(oferta.ceny.all())
            ostatnia_cena = ceny[-1] if ceny else None

            # Walidacja podstawowych danych
            if not oferta.adres or not oferta.metraz or not ostatnia_cena:
                logger.warning(f"Pominięto ofertę ID {oferta.id} z powodu brakujących danych")
                continue

            pomieszczenia = [
                {
                    "typ": p.typ,
                    "powierzchnia": float(p.powierzchnia),
                    "cena": float(p.cena)
                } for p in oferta.pomieszczenia.all()
            ]

            inne_swiadczenia = [
                {
                    "nazwa": s.nazwa,
                    "kwota": float(s.kwota),
                    "vat": s.vat_stawka
                } for s in oferta.swiadczenia.all()
            ]

            raport["oferty"].append({
                "id_oferty": oferta.id,
                "adres": oferta.adres,
                "lokalizacja": oferta.lokalizacja,
                "metraz_użytkowy": float(oferta.metraz),
                "liczba_pokoi": oferta.pokoje,
                "status": oferta.status,
                "cena_m2": float(oferta.cena_m2) if hasattr(oferta, "cena_m2") else None,
                "cena_całkowita": float(ostatnia_cena.kwota),
                "data_ceny": ostatnia_cena.data.isoformat(),
                "pomieszczenia_przynależne": pomieszczenia,
                "inne_swiadczenia": inne_swiadczenia,
                "data_aktualizacji": datetime.now().isoformat()
            })

        # Webhook testowy — możesz wygenerować swój na https://webhook.site
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url_api, headers=headers, data=json.dumps(raport))
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Raport wysłany pomyślnie"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Odpowiedź API: {response.status_code} - {response.text}"))
                logger.warning(f"API response: {response.status_code} - {response.text}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Błąd wysyłki raportu: {e}"))
            logger.error(f"Błąd wysyłki raportu: {e}")
