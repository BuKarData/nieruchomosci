from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Oferta, Cena
from .forms import OfertaForm, CenaForm

# Strona główna
def home(request):
    # Pobranie ostatnio dodanej inwestycji
    ostatnia_oferta = Oferta.objects.order_by('-data_dodania').first()
    return render(request, "home.html", {"ostatnia_oferta": ostatnia_oferta})

# Lista ofert
def lista_ofert(request):
    oferty = Oferta.objects.all().order_by('-data_dodania')
    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})

# Dodawanie oferty – formularz Django
def dodaj_oferte(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ofert')
    else:
        form = OfertaForm()
    return render(request, "oferty/dodaj_oferte.html", {"form": form})

# Dodawanie ceny dla oferty – poprawa CSRF
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

# Jeśli testujemy AJAX POST – trzeba dodać CSRF token
from django.http import JsonResponse

def ajax_dodaj_cene(request, oferta_id):
    if request.method == "POST" and request.headers.get('X-CSRFToken'):
        oferta = get_object_or_404(Oferta, id=oferta_id)
        kwota = request.POST.get("kwota")
        data = request.POST.get("data")
        Cena.objects.create(oferta=oferta, kwota=kwota, data=data)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "fail"}, status=403)
