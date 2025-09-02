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
        Każdy parametr w tabeli to nowa, oddzielna kolumna.
        """
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/Raport ofert firmy BZ-Bud.csv"

        # Zmiana kodowania na 'utf-8-sig', co dodaje BOM i zapewnia poprawną obsługę polskich znaków w Excelu
        with open(nazwa_pliku, "w", newline="", encoding="utf-8-sig") as csvfile:
            # Ujednolicona lista nagłówków kolumn
            fieldnames = [
                "nip", "regon", "nazwa_firmy", "adres_biura", "data_raportu",
                "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
                "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
                "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
                "pomieszczenia_przynalezne_nazwy", "rabaty_i_promocje_nazwy", "inne_swiadczenia_nazwy"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for oferta in oferty:
                ceny_list = list(oferta.ceny.all())
                ostatnia_cena = ceny_list[-1] if ceny_list else None
                cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else ""
                
                # Zbieranie nazw z powiązanych modeli i łączenie ich w jeden ciąg
                pomieszczenia = ", ".join([p.nazwa for p in oferta.pomieszczenia_przynalezne.all()])
                rabaty = ", ".join([r.nazwa for r in oferta.rabaty.all()])
                swiadczenia = ", ".join([s.nazwa for s in oferta.inne_swiadczenia.all()])

                # Słownik z danymi, którego klucze odpowiadają nagłówkom w `fieldnames`
                rekord_csv = {
                    "nip": dane_dewelopera["nip"],
                    "regon": dane_dewelopera["regon"],
                    "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                    "adres_biura": dane_dewelopera["adres_biura"],
                    "data_raportu": data_raportu,
                    "id_oferty": oferta.id,
                    "numer_lokalu": oferta.numer_lokalu,
                    "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else "",
                    "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else "",
                    "metraz": float(oferta.metraz) if oferta.metraz else "",
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena_pln": float(ostatnia_cena.kwota) if ostatnia_cena else "",
                    "cena_za_m2_pln": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else "",
                    "inwestycja_nazwa": oferta.inwestycja.nazwa if oferta.inwestycja else "",
                    "inwestycja_adres": oferta.inwestycja.adres if oferta.inwestycja else "",
                    "inwestycja_id": oferta.inwestycja.id if oferta.inwestycja else "",
                    "pomieszczenia_przynalezne_nazwy": pomieszczenia,
                    "rabaty_i_promocje_nazwy": rabaty,
                    "inne_swiadczenia_nazwy": swiadczenia,
                }
                writer.writerow(rekord_csv)

        self.stdout.write(self.style.SUCCESS(f"Raport CSV został pomyślnie wygenerowany: {nazwa_pliku}"))

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
            
            # Pobieranie powiązanych danych
            pomieszczenia_przynalezne = [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()]
            rabaty = [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ} for r in oferta.rabaty.all()]
            inne_swiadczenia = [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]

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
                        "streetAddress": oferta.inwestycja.adres if oferta.inwestycja else "",
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
                "pomieszczenia_przynaleznie": pomieszczenia_przynalezne,
                "rabaty": rabaty,
                "inne_swiadczenia": inne_swiadczenia,
            }
            # `ensure_ascii=False` jest kluczowe dla poprawnego kodowania znaków unicode w JSON
            raport_lines.append(json.dumps(rekord_jsonld, ensure_ascii=False))

        payload_jsonld = "\n".join(raport_lines)

        # Zmiana kodowania w trybie zapisu, aby upewnić się, że JSON-LD jest poprawny
        with open(nazwa_pliku, "w", encoding="utf-8") as f:
            f.write(payload_jsonld)
            
        self.stdout.write(self.style.SUCCESS(f"Raport JSON-LD został pomyślnie wygenerowany: {nazwa_pliku}"))

    def handle(self, *args, **kwargs):
        self.stdout.write("Rozpoczynanie generowania raportów...")

        dane_dewelopera = {
            "nip": "8261116680",         
            "regon": "540649478",        
            "nazwa_firmy": "B.Z-BUD Beata Żochowska",
            "adres_biura": "woj. MAZOWIECKIE, pow. wołomiński, gm. Zielonka, miejsc. Zielonka, ul. Ignacego Paderewskiego, nr 61, 05-220"
        }

        oferty = Oferta.objects.prefetch_related("ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia").all()
        
        if not oferty.exists():
            self.stdout.write(self.style.WARNING("Nie znaleziono żadnych ofert do zaraportowania."))
            return
            
        self.generate_csv_report(dane_dewelopera, oferty)
        self.generate_jsonld_report(dane_dewelopera, oferty)
        
        # Sekcja wysyłki JSONL do API - Ustrukturyzowanie i walidacja
        raport_lines = []
        data_raportu = str(date.today())

        for oferta in oferty:
            # Walidacja danych przed dodaniem do raportu
            if not oferta.inwestycja or not oferta.inwestycja.unikalny_identyfikator_przedsiewziecia:
                self.stdout.write(self.style.ERROR(f"Błąd walidacji: Oferta o ID {oferta.id} nie ma powiązanej inwestycji lub unikalnego identyfikatora."))
                continue

            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            
            if not ostatnia_cena:
                self.stdout.write(self.style.WARNING(f"Ostrzeżenie: Oferta o ID {oferta.id} nie ma zdefiniowanej ceny. Pomijam w raporcie JSONL."))
                continue

            cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else None

            # Spłaszczanie danych do pojedynczego rekordu JSON
            rekord_oferty = {
                "deweloper": {
                    "nip": dane_dewelopera["nip"],
                    "regon": dane_dewelopera["regon"],
                    "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                },
                "inwestycja": {
                    "unikalny_identyfikator": oferta.inwestycja.unikalny_identyfikator_przedsiewziecia,
                    "numer_pozwolenia_na_budowe": oferta.inwestycja.numer_pozwolenia,
                    "termin_rozpoczecia": oferta.inwestycja.termin_rozpoczecia.isoformat() if oferta.inwestycja.termin_rozpoczecia else None,
                    "termin_zakonczenia": oferta.inwestycja.termin_zakonczenia.isoformat() if oferta.inwestycja.termin_zakonczenia else None,
                },
                "oferta": {
                    "id": oferta.id,
                    "numer_lokalu": oferta.numer_lokalu,
                    "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else None,
                    "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else None,
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                },
                "dodatkowe_oplaty": {
                    "pomieszczenia_przynaleznie": [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()],
                    "rabaty_i_promocje": [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ, "data_od": r.data_od.isoformat(), "data_do": r.data_do.isoformat()} for r in oferta.rabaty.all()],
                    "inne_swiadczenia": [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]
                }
            }
            # `ensure_ascii=False` jest kluczowe dla poprawności znaków unicode w JSON
            raport_lines.append(json.dumps(rekord_oferty, ensure_ascii=False))

        if not raport_lines:
            self.stdout.write(self.style.WARNING("Brak poprawnych ofert do wysłania."))
            return

        payload = "\n".join(raport_lines)
        # Jawne ustawienie kodowania w nagłówku HTTP
        headers = {"Content-Type": "application/x-json-stream; charset=utf-8"}
        url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"

        try:
            response = requests.post(url_api, headers=headers, data=payload.encode('utf-8'))
            response.raise_for_status()
            self.stdout.write(self.style.SUCCESS(f"Raport JSONL wysłany pomyślnie, status: {response.status_code}"))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Błąd wysyłki raportu JSONL: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Wystąpił nieoczekiwany błąd: {e}"))