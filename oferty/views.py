# oferty/views.py
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.db.models import Prefetch

from .models import Inwestycja, Oferta


def _format_price(value):
    """Zwraca '300 000 zł' lub 'Brak'"""
    if value is None:
        return "Brak"
    try:
        q = Decimal(value)
        # zaokrąglamy do całych zł
        liczba = int(q)
        return f"{liczba:,}".replace(",", " ") + " zł"
    except (InvalidOperation, TypeError, ValueError):
        try:
            liczba = int(float(value))
            return f"{liczba:,}".replace(",", " ") + " zł"
        except Exception:
            return "Brak"


def _format_metraz(value):
    if value is None:
        return "Brak"
    try:
        return f"{float(value):.2f}"
    except Exception:
        return str(value)


def _status_badge(value):
    raw = (str(value) or "").lower()
    label = value
    css = "badge bg-success"
    if "sprzed" in raw:
        css = "badge bg-danger"
    elif "rezerw" in raw:
        css = "badge bg-warning text-dark"
    return (label, css)


def home(request):
    # Prefetch ofert, żeby zminimalizować zapytania
    oferty_qs = Oferta.objects.all().order_by("adres")
    inwestycje = Inwestycja.objects.prefetch_related(Prefetch("oferty", queryset=oferty_qs)).all()

    # Przygotuj pola do wyświetlenia w szablonie
    for inv in inwestycje:
        for of in inv.oferty.all():
            of.cena_str = _format_price(of.cena)
            of.metraz_str = _format_metraz(of.metraz)
            of.status_str, of.status_class = _status_badge(of.status)

    return render(request, "home.html", {"inwestycje": inwestycje})


def lista_ofert(request):
    oferty = Oferta.objects.select_related("inwestycja").order_by("-data_dodania")
    for of in oferty:
        of.cena_str = _format_price(of.cena)
        of.metraz_str = _format_metraz(of.metraz)
        of.status_str, of.status_class = _status_badge(of.status)
    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})



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
