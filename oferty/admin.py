from django.contrib import admin
from .models import Oferta, Inwestycja

class CenaInline(admin.TabularInline):
    model = Cena
    extra = 1

@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('inwestycja', 'adres', 'status', 'ostatnia_cena_display')
    list_filter = ('status', 'inwestycja')
    search_fields = ('adres',)
    inlines = [CenaInline]

    def ostatnia_cena_display(self, obj):
        ostatnia_cena = obj.ceny.order_by('-data').first()
        return f"{ostatnia_cena.kwota} zł" if ostatnia_cena else "Brak"
    ostatnia_cena_display.short_description = 'Aktualna cena'


@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis', 'zdjecie')
