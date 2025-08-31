# oferty/admin.py
from django.contrib import admin
from .models import Inwestycja, Oferta


class OfertaInline(admin.TabularInline):
    model = Oferta
    extra = 0
    fields = ("adres", "metraz", "cena", "status", "pokoje", "zdjecie")
    show_change_link = True


@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ("nazwa", "opis")
    search_fields = ("nazwa",)
    inlines = [OfertaInline]


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("adres", "inwestycja", "metraz", "cena", "status", "pokoje", "data_dodania")
    list_filter = ("status", "inwestycja")
    search_fields = ("adres",)
