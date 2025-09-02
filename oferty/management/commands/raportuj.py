import json
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from oferty.models import Oferta

class Command(BaseCommand):
    help = "Generuje raport ofert w formacie JSON-LD zgodnym z art. 19b ustawy i wysyła przez API"

    def handle(self, *args, **kwargs):
        oferty = Oferta.objects.prefetch_related("ceny", "pomieszczenia", "swiadczenia").all()

        raport = {
            "@context": {
                "schema": "https://schema.org/",
                "adres": "schema:address",
                "lokalizacja": "schema:location",
                "metraz": "schema:floorSize",
                "pokoje": "schema:numberOfRooms",
                "status": "schema:availability",
                "cena": "schema:price",
                "cena_m2": "schema:pricePerUnit",
                "data_ceny": "schema:priceValidUntil",
                "pomieszczenia_typ": "schema:hasPart",
                "pomieszczenia_powierzchnia": "schema:area",
                "pomieszczenia_cena": "schema:price",
                "swiadczenie_nazwa": "schema:name",
                "swiadczenie_kwota": "schema:value",
                "swiadczenie_vat": "schema:taxRate",
                "data_aktualizacji": "schema:dateModified"
            },
            "@type": "schema:OfferCatalog",
            "data_raportu": datetime.now().isoformat(),
            "źródło": "https://www.bzbud.pl",
            "oferty": []
        }

        for oferta in oferty:
            cena_obj = oferta.ceny.last()
            pom = oferta.pomieszczenia.first()
            sw = oferta.swiadczenia.first()

            oferta_jsonld = {
                "@type": "schema:Offer",
                "@id": f"https://www.bzbud.pl/oferta/{oferta.id}",
                "adres": oferta.adres,
                "lokalizacja": oferta.lokalizacja,
                "metraz": float(oferta.metraz),
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": float(cena_obj.kwota) if cena_obj else None,
                "cena_m2": float(oferta.cena_m2) if oferta.cena_m2 else None,
                "data_ceny": cena_obj.data.isoformat() if cena_obj else None,
                "pomieszczenia_typ": pom.typ if pom else None,
                "pomieszczenia_powierzchnia": float(pom.powierzchnia) if pom else None,
                "pomieszczenia_cena": float(pom.cena) if pom else None,
                "swiadczenie_nazwa": sw.nazwa if sw else None,
                "swiadczenie_kwota": float(sw.kwota) if sw else None,
                "swiadczenie_vat": sw.vat_stawka if sw else None,
                "data_aktualizacji": oferta.data_aktualizacji.isoformat()
            }

            raport["oferty"].append(oferta_jsonld)

        # Wysyłka JSON-LD przez API
        url = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
        headers = {"Content-Type": "application/ld+json"}

        response = requests.post(url, headers=headers, data=json.dumps(raport))
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("✅ JSON-LD wysłany pomyślnie"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Błąd: {response.status_code} - {response.text}"))
