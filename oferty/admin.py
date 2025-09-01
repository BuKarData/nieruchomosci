from django.contrib import admin
from .models import Oferta, Cena, Inwestycja

#admin.site.register(Oferta)
#admin.site.register(Cena)


@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ("nazwa", "adres", "data_dodania")
    search_fields = ("nazwa", "adres")


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("adres", "metraz", "pokoje", "status", "data_dodania")
    list_filter = ("status",)
    search_fields = ("adres",)


@admin.register(Cena)
class CenaAdmin(admin.ModelAdmin):
    list_display = ("oferta", "kwota", "data")
    list_filter = ("data",)
