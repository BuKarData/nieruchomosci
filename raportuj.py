from django.shortcuts import render
from .models import Oferta
import requests
import json
from datetime import date

def lista_ofert(request):
    oferty = Oferta.objects.prefetch_related("ceny").all()

    # Przygotowanie danych do wyświetlenia (tabela + wykres)
    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        for cena in ceny_list:
            cena.kwota_int = int(cena.kwota.replace(" ", "").replace("zł", ""))
        oferta.ceny_list = ceny_list
        oferta.ostatnia_cena = ceny_list[-1] if ceny_list else None

    # --- AUTOMATYCZNE WYSYŁANIE RAPORTU ---
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
            "cena": ostatnia_cena.kwota if ostatnia_cena else None,
            "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
        })

    # Wysyłka raportu do mockowego API (lub prawdziwego)
    url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"  # lub prawdziwe API
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url_api, headers=headers, data=json.dumps(raport))
        print("Raport wysłany, status:", response.status_code)
    except Exception as e:
        print("Błąd wysyłki raportu:", e)
    # --- KONIEC WYSYŁKI RAPORTU ---

    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})
