# raportuj.py
import os
import django
import requests
import json
from datetime import date

# --- konfiguracja Django w skrypcie standalone ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nieruchomosci.settings")
django.setup()

from oferty.models import Oferta

def wyslij_raport():
    oferty = Oferta.objects.prefetch_related("ceny").all()

    raport = {
        "data": str(date.today()),
        "oferty": []
    }

    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        if ceny_list:
            ostatnia_cena = ceny_list[-1]
            try:
                kwota = float(str(ostatnia_cena.kwota).replace(" ", "").replace("zł", ""))
            except (ValueError, TypeError):
                kwota = None
            raport["oferty"].append({
                "id": oferta.id,
                "adres": oferta.adres,
                "metraz": oferta.metraz,
                "pokoje": oferta.pokoje,
                "status": oferta.status,
                "cena": kwota,
                "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            })

    # Wyślij raport jednym POST
    url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"  # zamień na prawdziwe API
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url_api, headers=headers, data=json.dumps(raport))
        print(f"Raport wysłany, status: {response.status_code}")
    except Exception as e:
        print("Błąd wysyłki raportu:", e)

if __name__ == "__main__":
    wyslij_raport()
