from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from .forms import OfertaForm, CenaForm


# Strona główna
#def home(request):
 #   ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()
  #  return render(request, "home.html", {"ostatnia_oferta": ostatnia_oferta})

def home(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    
    inwestycje = Inwestycja.objects.prefetch_related(
        Prefetch('oferta_set', queryset=Oferta.objects.prefetch_related(ceny_prefetch))
    ).order_by('-data_dodania')

    # Przygotowanie danych dla każdej oferty
    for inwestycja in inwestycje:
        for oferta in inwestycja.oferta_set.all():
            ceny = list(oferta.ceny.all())
            if ceny:
                ostatnia = ceny[-1]
                oferta.ostatnia_cena = ostatnia.kwota
                oferta.cena_m2 = float(oferta.ostatnia_cena) / float(oferta.metraz) if oferta.metraz else None
            else:
                oferta.ostatnia_cena = None
                oferta.cena_m2 = None

    return render(request, "home.html", {"inwestycje": inwestycje})


# Lista ofert
from django.shortcuts import render
from django.db.models import Prefetch


def lista_ofert(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    oferty = Oferta.objects.all().prefetch_related(ceny_prefetch).order_by('-data_dodania')

    for oferta in oferty:
        ceny = list(oferta.ceny.all())
        oferta.ceny_list = []  # lista dla historii cen

        for c in ceny:
            try:
                kwota = float(c.kwota)
                oferta.ceny_list.append({'kwota': kwota, 'data': c.data})
            except (ValueError, TypeError):
                continue

        if oferta.ceny_list:
            ostatnia = oferta.ceny_list[-1]
            oferta.ostatnia_cena = ostatnia
            oferta.cena_m2 = int(ostatnia['kwota'] / float(oferta.metraz)) if oferta.metraz else None
        else:
            oferta.ostatnia_cena = None
            oferta.cena_m2 = None

        oferta.chart_data = {
            "labels": [str(c['data']) for c in oferta.ceny_list],
            "data": [c['kwota'] for c in oferta.ceny_list],
        }
        
    

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