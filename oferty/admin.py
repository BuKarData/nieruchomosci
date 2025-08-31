from django.contrib import admin
from .models import Inwestycja, Oferta

@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ("nazwa", "adres", "data_dodania")
    search_fields = ("nazwa", "adres")
    list_filter = ("data_dodania",)


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("adres", "inwestycja", "metraz", "pokoje", "status", "ostatnia_cena", "cena_m2")
    list_filter = ("status", "inwestycja")
    search_fields = ("adres", "inwestycja__nazwa")
