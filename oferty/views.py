from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import Oferta, Cena, Inwestycja
from .forms import OfertaForm, CenaForm


# Strona główna
#def home(request):
 #   ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()
  #  return render(request, "home.html", {"ostatnia_oferta": ostatnia_oferta})

from decimal import Decimal

# Lista ofert
from django.shortcuts import render



def home(request):
    # Pobranie wszystkich inwestycji
    inwestycje = Inwestycja.objects.all()

    # Dla każdej inwestycji pobieramy powiązane oferty i ceny
    for inwestycja in inwestycje:
        oferty_prefetch = Prefetch('oferta_set', queryset=Oferta.objects.prefetch_related(
            Prefetch('ceny', queryset=Cena.objects.order_by('data'))
        ))
        inwestycja.oferty = inwestycja.oferta_set.prefetch_related(oferty_prefetch).all()

        # Przygotowanie danych dla każdej oferty
        for oferta in inwestycja.oferty:
            ceny = list(oferta.ceny.all())
            oferta.ostatnia_cena = ceny[-1] if ceny else None

            # Cena
            if oferta.ostatnia_cena and oferta.ostatnia_cena.kwota is not None:
                kwota = oferta.ostatnia_cena.kwota
                try:
                    kwota_int = int(Decimal(kwota))
                except:
                    kwota_int = None
                oferta.ostatnia_cena_str = f"{kwota_int:,}".replace(",", " ") + " zł" if kwota_int else "Brak"
            else:
                oferta.ostatnia_cena_str = "Brak"

            # Cena za m²
            if oferta.ostatnia_cena and oferta.metraz:
                try:
                    cena_m2 = int(Decimal(oferta.ostatnia_cena.kwota) / Decimal(oferta.metraz))
                    oferta.cena_m2_str = f"{cena_m2:,}".replace(",", " ") + " zł/m²"
                except:
                    oferta.cena_m2_str = "Brak"
            else:
                oferta.cena_m2_str = "Brak"

            # Metraż
            oferta.metraz_str = f"{float(oferta.metraz):.2f}" if oferta.metraz else "Brak"

            # Status
            raw_status = (str(oferta.status) or "").lower()
            oferta.status_str = oferta.get_status_display() if hasattr(oferta, "get_status_display") else raw_status.capitalize()
            if "sprzed" in raw_status:
                oferta.status_class = "badge bg-danger"
            elif "rezerw" in raw_status:
                oferta.status_class = "badge bg-warning text-dark"
            else:
                oferta.status_class = "badge bg-success"

    return render(request, "home.html", {"inwestycje": inwestycje})

def lista_ofert(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    oferty = Oferta.objects.all().prefetch_related(ceny_prefetch).order_by('-data_dodania')

    for oferta in oferty:
        ceny = list(oferta.ceny.all())
        oferta.ostatnia_cena = ceny[-1] if ceny else None

        # Cena
        if oferta.ostatnia_cena and oferta.ostatnia_cena.kwota is not None:
            try:
                kwota_int = int(Decimal(oferta.ostatnia_cena.kwota))
            except:
                kwota_int = None
            oferta.ostatnia_cena_str = f"{kwota_int:,}".replace(",", " ") + " zł" if kwota_int else "Brak"
        else:
            oferta.ostatnia_cena_str = "Brak"

        # Cena za m²
        if oferta.ostatnia_cena and oferta.metraz:
            try:
                cena_m2 = int(Decimal(oferta.ostatnia_cena.kwota) / Decimal(oferta.metraz))
                oferta.cena_m2_str = f"{cena_m2:,}".replace(",", " ") + " zł/m²"
            except:
                oferta.cena_m2_str = "Brak"
        else:
            oferta.cena_m2_str = "Brak"

        oferta.metraz_str = f"{float(oferta.metraz):.2f}" if oferta.metraz else "Brak"

    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})





# Dodawanie oferty
def dodaj_oferte(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ofert')
    else:
        form = OfertaForm()
    return render(request, "oferty/dodaj_oferte.html", {"form": form})


# Dodawanie ceny
def dodaj_cene(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    if request.method == "POST":
        form = CenaForm(request.POST)
        if form.is_valid():
            cena = form.save(commit=False)
            cena.oferta = oferta
            cena.save()
            return redirect('lista_ofert')
    else:
        form = CenaForm()
    return render(request, "oferty/dodaj_cene.html", {"form": form, "oferta": oferta})


# AJAX dodawanie ceny
@csrf_exempt
def ajax_dodaj_cene(request, oferta_id):
    if request.method == "POST":
        oferta = get_object_or_404(Oferta, id=oferta_id)
        kwota = safe_float(request.POST.get("kwota"))
        data = request.POST.get("data")
        if kwota is not None and data:
            Cena.objects.create(oferta=oferta, kwota=kwota, data=data)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "fail"}, status=400)


# --- Pomocnicza funkcja do bezpiecznej konwersji kwoty ---
def safe_float(value):
    """
    Konwertuje wartość na float, usuwa spacje i przecinki.
    Zwraca None jeśli konwersja się nie powiedzie.
    """
    if value is None:
        return None
    try:
        return float(str(value).replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return None
