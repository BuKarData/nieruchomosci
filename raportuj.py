# raportuj.py
import requests
import logging
from datetime import date

logger = logging.getLogger(__name__)

def wyslij_raport(oferty):
    raport = {
        "data": str(date.today()),
        "oferty": []
    }

    for oferta in oferty:
        ostatnia_cena = oferta.ostatnia_cena
        raport["oferty"].append({
            "id": oferta.id,
            "adres": oferta.adres,
            "metraz": oferta.metraz,
            "pokoje": oferta.pokoje,
            "status": oferta.status,
            "cena": str(ostatnia_cena.kwota) if ostatnia_cena else None,
            "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
        })

    url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
    try:
        response = requests.post(url_api, json=raport, timeout=10)
        logger.info("Raport wysłany. Status: %s", response.status_code)
    except Exception as e:
        logger.error("Błąd wysyłki raportu: %s", e)
