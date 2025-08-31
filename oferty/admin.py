from django.contrib import admin
from .models import Oferta, Inwestycja

# Rejestracja modelu Inwestycja
@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis', 'zdjecie', 'data_dodania')  # tylko istniejące pola
    search_fields = ('nazwa', 'opis')
    list_filter = ('data_dodania',)  # tylko pola typu DateField/DateTimeField

# Rejestracja modelu Oferta
@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('adres', 'metraz', 'pokoje', 'status', 'inwestycja')
    search_fields = ('adres',)
    list_filter = ('status', 'inwestycja')
