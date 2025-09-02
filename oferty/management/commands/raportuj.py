from django.core.management.base import BaseCommand
from oferty.models import Oferta
import requests
import json
from datetime import date
import csv
import os
from openpyxl import Workbook


class Command(BaseCommand):
    help = "Generuje dzienny raport ofert w formatach JSONL/JSON-LD, CSV i XLSX, a następnie wysyła go do API."

    def generate_csv_report(self, dane_dewelopera, oferty):
        """
        Generuje raport w formacie CSV.
        """
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/Raport ofert firmy BZ-Bud_{data_raportu}.csv"

        # Ustalenie maksymalnej liczby elementów w listach
        max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
        max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
        max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

        fieldnames = [
            "nip", "regon", "nazwa_firmy", "adres_biura",
            "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
            "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
            "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
        ]
        fieldnames += [f"pomieszczenie_{i+1}" for i in range(max_pom)]
        fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
        fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

        with open(nazwa_pliku, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for rekord_csv in self._build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
                writer.writerow(rekord_csv)

        self.stdout.write(self.style.SUCCESS(f"Raport CSV został pomyślnie wygenerowany: {nazwa_pliku}"))

    def generate_xlsx_report(self, dane_dewelopera, oferty):
        """
        Generuje raport w formacie XLSX.
        """
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        nazwa_pliku = f"{raporty_dir}/Raport ofert firmy BZ-Bud_{data_raportu}.xlsx"

        # Ustalenie maksymalnej liczby elementów w listach
        max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
        max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
        max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

        fieldnames = [
            "nip", "regon", "nazwa_firmy", "adres_biura",
            "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
            "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
            "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
        ]
        fieldnames += [f"pomieszczenie_{i+1}" for i in range(max_pom)]
        fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
        fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

        wb = Workbook()
        ws = wb.active
        ws.title = "Raport ofert"

        # Nagłówki
        ws.append(fieldnames)

        # Dane
        for rekord in self._build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
            row = [rekord.get(field, "") for field in fieldnames]
            ws.append(row)

        wb.save(nazwa_pliku)
        self.stdout.write(self.style.SUCCESS(f"Raport XLSX został pomyślnie wygenerowany: {nazwa_pliku}"))

    def _build_flattened_records(self, dane_dewelopera, oferty, max_pom, max_rab, max_swi):
        """
        Generator zwracający spłaszczone rekordy do CSV/XLSX.
        """
        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = (float(ostatnia_cena.kwota) / float(oferta.metraz)) if ostatnia_cena and oferta.metraz else ""

            rekord_csv = {
                "nip": dane_dewelopera["nip"],
                "regon": dane_dewelopera["regon"],
                "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
                "adres_biura": dane_dewelopera["adres_biura"],
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
            }

            # Rozwój list na osobne kolumny
            for i, p in enumerate(oferta.pomieszczenia_przynalezne.all()):
                rekord_csv[f"pomieszczenie_{i+1}"] = p.nazwa
            for i, r in enumerate(oferta.rabaty.all()):
                rekord_csv[f"rabat_{i+1}"] = r.nazwa
            for i, s in enumerate(oferta.inne_swiadczenia.all()):
                rekord_csv[f"swiadczenie_{i+1}"] = s.nazwa

            yield rekord_csv

    def generate_jsonld_report(self, dane_dewelopera, oferty):
        # (pozostaje bez zmian)
        ...

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
        self.generate_xlsx_report(dane_dewelopera, oferty)
        self.generate_jsonld_report(dane_dewelopera, oferty)

        # (sekcja wysyłki JSONL pozostaje bez zmian)
        ...
