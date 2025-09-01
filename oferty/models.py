from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import Inwestycja, Oferta, Cena
from .forms import OfertaForm, CenaForm


# --- Strona główna: pokaz ostatnią ofertę ---
def home(request):
    ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()

    if ostatnia_oferta:
        # Status CSS i tekst
        ostatnia_oferta.status_class = f"status-{ostatnia_oferta.status.lower()}"
        ostatnia_oferta.status_str = ostatnia_oferta.status.title()

        # Metraż jako string
        ostatnia_oferta.metraz_str = f"{ostatnia_oferta.metraz:.2f}" if ostatnia_oferta.metraz else "Brak"

        # Ostatnia cena i cena za m²
        ostatnia_cena = ostatnia_oferta.ceny.order_by('-data').first()
        if ostatnia_cena:
            kwota = float(ostatnia_cena.kwota)
            ostatnia_oferta.ostatnia_cena_str = f"{int(kwota):,} zł ({ostatnia_cena.data})"
            if ostatnia_oferta.metraz:
                cena_m2 = int(kwota / float(ostatnia_oferta.metraz))
                ostatnia_oferta.cena_m2_str = f"{cena_m2:,} zł/m²"
            else:
                ostatnia_oferta.cena_m2_str = "Brak"
        else:
            ostatnia_oferta.ostatnia_cena_str = "Brak"
            ostatnia_oferta.cena_m2_str = "Brak"

    return render(request, "home.html", {"ostatnia_oferta": ostatnia_oferta})


# --- Lista inwestycji z ofertami ---
def lista_inwestycji(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    oferty_prefetch = Prefetch('oferta_set', queryset=Oferta.objects.prefetch_related(ceny_prefetch))
    
    inwestycje = Inwestycja.objects.prefetch_related(
        Prefetch('oferty', queryset=Oferta.objects.prefetch_related(ceny_prefetch))
    ).order_by('-data_dodania')

    for inwestycja in inwestycje:
        for oferta in inwestycja.oferty.all():
            ceny = list(oferta.ceny.all())
            if ceny:
                ostatnia = ceny[-1]
                oferta.ostatnia_cena = ostatnia.kwota
                if oferta.metraz:
                    oferta.cena_m2 = float(oferta.ostatnia_cena) / float(oferta.metraz)
                else:
                    oferta.cena_m2 = None
            else:
                oferta.ostatnia_cena = None
                oferta.cena_m2 = None

    return render(request, "oferty/lista_inwestycji.html", {"inwestycje": inwestycje})


# --- Dodawanie oferty ---
def dodaj_oferte(request):
    if request.method == "POST":
        form = OfertaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_inwestycji')
    else:
        form = OfertaForm()
    return render(request, "oferty/dodaj_oferte.html", {"form": form})


# --- Dodawanie ceny ---
def dodaj_cene(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    if request.method == "POST":
        form = CenaForm(request.POST)
        if form.is_valid():
            cena = form.save(commit=False)
            cena.oferta = oferta
            cena.save()
            return redirect('lista_inwestycji')
    else:
        form = CenaForm()
    return render(request, "oferty/dodaj_cene.html", {"form": form, "oferta": oferta})


# --- AJAX dodawanie ceny ---
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


# --- Pomocnicza funkcja do konwersji kwoty ---
def safe_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return None
