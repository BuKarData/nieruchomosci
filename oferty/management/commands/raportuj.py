# /twoj_projekt/nazwa_aplikacji/management/commands/raportuj.py

from django.core.management.base import BaseCommand
from oferty.models import Oferta
import requests
import json
from datetime import date

class Command(BaseCommand):
    help = "Generuje dzienny raport ofert w formacie JSONL i wysyła go do API zgodnie z wymogami ustawy."

    def handle(self, *args, **kwargs):

        dane_dewelopera = {
            "nip": "8261116680",         
            "regon": "540649478",        
            "nazwa_firmy": "B.Z­BUD Beata Żochowska",
            "adres_biura": "woj. MAZOWIECKIE, pow. wołomiński, gm. Zielonka, miejsc. Zielonka, ul. Ignacego Paderewskiego, nr 61, 05-220"
            }

        # Pobieranie ofert wraz z powiązanymi cenami
        oferty = Oferta.objects.prefetch_related("ceny").all()
        
        # Lista do przechowywania pojedynczych linii JSON
        raport_lines = []
        data_raportu = str(date.today())

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None

            # Tworzenie pojedynczego rekordu dla formatu JSONL
            rekord_oferty = {
                **dane_dewelopera,  # Dodanie danych firmy do rekordu
                "data_raportu": data_raportu,
                "oferta": {
                    "id": oferta.id,
                    "adres": oferta.adres,
                    "numer_lokalu": oferta.numer_lokalu,
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                }
            }
            # Konwersja słownika do stringa JSON i dodanie do listy
            raport_lines.append(json.dumps(rekord_oferty))

        # Przygotowanie i wysyłka payloadu w formacie JSONL
        payload = "\n".join(raport_lines)
        
        headers = {"Content-Type": "application/x-json-stream"}
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"  # zamień na własny endpoint

        if not payload:
            self.stdout.write(self.style.WARNING("Nie znaleziono żadnych ofert do zaraportowania."))
            return

        try:
            # Wysyłka danych zakodowanych w UTF-8
            response = requests.post(url_api, headers=headers, data=payload.encode('utf-8'))
            response.raise_for_status() # Rzuci wyjątkiem dla statusów 4xx/5xx
            self.stdout.write(self.style.SUCCESS(f"Raport wysłany pomyślnie, status: {response.status_code}"))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Wystąpił nieoczekiwany błąd: {e}"))