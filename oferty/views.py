from django.shortcuts import render
from .models import Oferta



def home(request):
    ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()
    if ostatnia_oferta:
        ceny_list = list(ostatnia_oferta.ceny.all())
        ostatnia_oferta.ostatnia_cena = ceny_list[-1] if ceny_list else None

        # formatowanie ceny
        if ostatnia_oferta.ostatnia_cena:
            kwota = int(ostatnia_oferta.ostatnia_cena.kwota)  # <- konwersja na int
            ostatnia_oferta.ostatnia_cena_str = f"{kwota:,}".replace(",", " ")
        else:
            ostatnia_oferta.ostatnia_cena_str = "Brak"

    return render(request, 'oferty/home.html', {'ostatnia_oferta': ostatnia_oferta})



# pobranie ostatnio dodanej oferty po dacie dodania




def lista_ofert(request):
    # Pobieramy wszystkie oferty wraz z powiązanymi cenami
    oferty = Oferta.objects.prefetch_related("ceny").all()

    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())

        for cena in ceny_list:
            # konwertujemy na int i zapisujemy w nowym polu
            kwota_int = int(cena.kwota.replace(" ", "").replace("zł", ""))
            cena.kwota_int = kwota_int
            # formatowanie z separatorem tysięcy
            cena.kwota_str = f"{kwota_int:,}".replace(",", " ")

        oferta.ceny_list = ceny_list
        oferta.ostatnia_cena = ceny_list[-1] if ceny_list else None

        if oferta.ostatnia_cena:
            oferta.ostatnia_cena_str = f"{oferta.ostatnia_cena.kwota_int:,}".replace(",", " ") + " zł" + f" ({oferta.ostatnia_cena.data})"
        else:
            oferta.ostatnia_cena_str = "Brak"


    # historia cen jako lista stringów
        oferta.historia_cen_str = [
            f"{cena.kwota_str} zł ({cena.data})" for cena in ceny_list
        ] if ceny_list else ["Brak"]

    status_map = {
        "dostępne": "status-dostępne",
        "rezerwacja": "status-rezerwacja",
        "sprzedane": "status-sprzedane"
    }

    for oferta in oferty:
        oferta.status_str = oferta.status.capitalize()
        oferta.status_class = status_map.get(oferta.status.lower(), "")


    import json

    # dane do wykresu
    oferta.chart_data = json.dumps({
        "labels": [cena.data.isoformat() for cena in ceny_list],
        "data": [cena.kwota_int for cena in ceny_list]
    })

    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())

    # ostatnia cena (jeśli jest)
        oferta.ostatnia_cena = ceny_list[-1] if ceny_list else None

        if oferta.ostatnia_cena:
        # cena w int
            kwota_int = int(str(oferta.ostatnia_cena.kwota).replace(" ", "").replace("zł", ""))

        # cena za m² (float -> zaokrąglone do 0 miejsca)
            try:
                metraz_float = float(oferta.metraz)
                cena_m2 = round(kwota_int / metraz_float)
                oferta.cena_m2_str = f"{cena_m2:,}".replace(",", " ") + " zł/m²"
            except (ValueError, ZeroDivisionError):
                oferta.cena_m2_str = "Brak"
        else:
            oferta.cena_m2_str = "Brak"



    
    for oferta in oferty:
        try:
            metraz_float = float(oferta.metraz)
            oferta.metraz_str = f"{metraz_float:.1f} m²"
        except (ValueError, TypeError):
        # Jeśli nie da się przekonwertować, pokazujemy "Brak"
            oferta.metraz_str = "Brak"

   

    # Wysyłka raportu (do testów można użyć webhook.site)
    url_api = "https://webhook.site/63ac4048-0ef4-4847-8787-0fff7d401940"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url_api, headers=headers, data=json.dumps(raport))
        print("Raport wysłany, status:", response.status_code)
    except Exception as e:
        print("Błąd wysyłki raportu:", e)

    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})
