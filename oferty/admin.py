from django.contrib import admin
from .models import Inwestycja, Oferta


@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ("nazwa", "opis", "zdjecie")
    search_fields = ("nazwa",)


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("adres", "metraz", "cena", "status", "pokoje", "inwestycja")
    list_filter = ("status", "inwestycja")
    search_fields = ("adres",)
