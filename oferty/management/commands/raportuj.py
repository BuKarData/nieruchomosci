from django.core.management.base import BaseCommand
from oferty.models import Oferta
import requests
import json
from datetime import date
import csv
import os

class Command(BaseCommand):
    help = "Generuje dzienny raport ofert w formatach JSONL/JSON-LD i CSV, a następnie wysyła go do API."

    def generate_csv_report(self, dane_dewelopera, oferty):
        """
        Generuje raport w formacie CSV i zapisuje go w pliku.
        """
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/raport_{data_raportu}.csv"

        with open(nazwa_pliku, "w", newline="", encoding="utf-8") as csvfile:
            # Nagłówki kolumn w pliku CSV
            fieldnames = [
                "nip", "regon", "nazwa_firmy", "adres_biura", "data_raportu",
                "id_oferty", "adres_inwestycji", "numer_lokalu", "numer_oferty",
                "metraz", "pokoje", "status", "cena", "cena_za_m2", "data_ceny",
                "pomieszczenia_przynaleznie", "rabaty_i_promocje", "inne_swiadczenia"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for oferta in oferty:
                ceny_list = list(oferta.ceny.all())
                ostatnia_cena = ceny_list[-1] if ceny_list else None
                cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else ""
                
                rekord_csv = {
                    "nip": dane_dewelopera["nip"],
                    "regon": dane_dewelopera["regon"],
                    "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                    "adres_biura": dane_dewelopera["adres_biura"],
                    "data_raportu": data_raportu,
                    "id_oferty": oferta.id,
                    "adres_inwestycji": oferta.adres_inwestycji if hasattr(oferta, 'adres_inwestycji') else "",
                    "numer_lokalu": oferta.numer_lokalu,
                    "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else "",
                    "metraz": float(oferta.metraz) if oferta.metraz else "",
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else "",
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else "",
                    "pomieszczenia_przynaleznie": oferta.pomieszczenia_przynaleznie if hasattr(oferta, 'pomieszczenia_przynaleznie') else "",
                    "rabaty_i_promocje": oferta.rabaty_i_promocje if hasattr(oferta, 'rabaty_i_promocje') else "",
                    "inne_swiadczenia": oferta.inne_swiadczenia if hasattr(oferta, 'inne_swiadczenia') else ""
                }
                writer.writerow(rekord_csv)

        self.stdout.write(self.style.SUCCESS(f"Raport CSV został pomyślnie wygenerowany: {nazwa_pliku}"))

    ---

    def generate_jsonld_report(self, dane_dewelopera, oferty):
        """
        Generuje raport w formacie JSON-LD.
        """
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/raport_{data_raportu}.jsonld"
        
        raport_lines = []
        
        jsonld_context = {
            "@vocab": "http://schema.org/",
            "nip": "http://purl.org/nace/NACE2/82.6",
            "regon": "http://purl.org/nace/NACE2/54.0",
            "metraz": "http://purl.org/qudt/vocab/area",
            "cena": "http://purl.org/qudt/vocab/currency",
            "data_raportu": "http://purl.org/dc/terms/date",
        }

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else None

            rekord_jsonld = {
                "@context": jsonld_context,
                "@type": "Product",
                "name": f"Oferta nr {oferta.numer_oferty}",
                "description": f"Mieszkanie {oferta.pokoje}-pokojowe o metrażu {oferta.metraz} m2.",
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "PLN",
                    "price": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "validFrom": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                },
                "itemOffered": {
                    "@type": "Apartment",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": oferta.adres_inwestycji if hasattr(oferta, 'adres_inwestycji') else "",
                        "addressLocality": "Zielonka",
                    },
                    "numberOfRooms": oferta.pokoje,
                    "floorSize": {
                        "@type": "QuantitativeValue",
                        "value": float(oferta.metraz) if oferta.metraz else None,
                        "unitCode": "m2"
                    },
                    "status": oferta.status
                },
                "seller": {
                    "@type": "Organization",
                    "name": dane_dewelopera["nazwa_firmy"],
                    "vatID": dane_dewelopera["nip"],
                    "taxID": dane_dewelopera["regon"],
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": dane_dewelopera["adres_biura"],
                    }
                },
                "data_raportu": data_raportu,
                "cena_za_m2": cena_m2,
                "pomieszczenia_przynaleznie": oferta.pomieszczenia_przynaleznie if hasattr(oferta, 'pomieszczenia_przynaleznie') else None,
                "rabaty_i_promocje": oferta.rabaty_i_promocje if hasattr(oferta, 'rabaty_i_promocje') else None,
                "inne_swiadczenia": oferta.inne_swiadczenia if hasattr(oferta, 'inne_swiadczenia') else None
            }
            raport_lines.append(json.dumps(rekord_jsonld, ensure_ascii=False))

        payload_jsonld = "\n".join(raport_lines)

        with open(nazwa_pliku, "w", encoding="utf-8") as f:
            f.write(payload_jsonld)
            
        self.stdout.write(self.style.SUCCESS(f"Raport JSON-LD został pomyślnie wygenerowany: {nazwa_pliku}"))

    ---

    def handle(self, *args, **kwargs):
        self.stdout.write("Rozpoczynanie generowania raportów...")

        dane_dewelopera = {
            "nip": "8261116680",         
            "regon": "540649478",        
            "nazwa_firmy": "B.Z­BUD Beata Żochowska",
            "adres_biura": "woj. MAZOWIECKIE, pow. wołomiński, gm. Zielonka, miejsc. Zielonka, ul. Ignacego Paderewskiego, nr 61, 05-220"
        }

        oferty = Oferta.objects.prefetch_related("ceny").all()
        
        if not oferty.exists():
            self.stdout.write(self.style.WARNING("Nie znaleziono żadnych ofert do zaraportowania."))
            return
            
        self.generate_csv_report(dane_dewelopera, oferty)
        self.generate_jsonld_report(dane_dewelopera, oferty)
        
        # Sekcja wysyłki JSONL do API
        raport_lines = []
        data_raportu = str(date.today())

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else None

            rekord_oferty = {
                **dane_dewelopera,
                "data_raportu": data_raportu,
                "oferta": {
                    "id": oferta.id,
                    "adres": oferta.adres,
                    "numer_lokalu": oferta.numer_lokalu,
                    "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else None,
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None,
                    "pomieszczenia_przynaleznie": oferta.pomieszczenia_przynaleznie if hasattr(oferta, 'pomieszczenia_przynaleznie') else None,
                    "rabaty_i_promocje": oferta.rabaty_i_promocje if hasattr(oferta, 'rabaty_i_promocje') else None,
                    "inne_swiadczenia": oferta.inne_swiadczenia if hasattr(oferta, 'inne_swiadczenia') else None
                }
            }
            raport_lines.append(json.dumps(rekord_oferty))

        payload = "\n".join(raport_lines)
        headers = {"Content-Type": "application/x-json-stream"}
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"

        try:
            response = requests.post(url_api, headers=headers, data=payload.encode('utf-8'))
            response.raise_for_status()
            self.stdout.write(self.style.SUCCESS(f"Raport JSONL wysłany pomyślnie, status: {response.status_code}"))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu JSONL: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Wystąpił nieoczekiwany błąd: {e}"))