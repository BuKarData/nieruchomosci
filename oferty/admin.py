from django.contrib import admin
from .models import Oferta, Inwestycja

# Rejestracja modelu Inwestycja
@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'adres', 'data_dodania')
    search_fields = ('nazwa', 'adres')
    list_filter = ('data_dodania',)

# Rejestracja modelu Oferta
@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('adres', 'metraz', 'pokoje', 'status', 'inwestycja')
    search_fields = ('adres',)
    list_filter = ('status', 'inwestycja')
