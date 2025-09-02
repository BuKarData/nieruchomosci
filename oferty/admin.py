from django.contrib import admin
from .models import Oferta, Cena, Inwestycja, InwestycjaZdjecie


@admin.register(InwestycjaZdjecie)
class InwestycjaZdjecieAdmin(admin.ModelAdmin):
    list_display = ('obraz', 'inwestycja_nazwa')

    def inwestycja_nazwa(self, obj):
        return obj.inwestycja.nazwa if obj.inwestycja else "Brak inwestycji"
    
    inwestycja_nazwa.short_description = "Inwestycja"


class InwestycjaZdjecieInline(admin.TabularInline):
    model = InwestycjaZdjecie
    extra = 1
    fields = ('obraz', 'inwestycja_nazwa')
    readonly_fields = ('inwestycja_nazwa',)

    def inwestycja_nazwa(self, obj):
        # This method safely returns the name of the related investment.
        # It won't crash even if 'obj.inwestycja' is None.
        return obj.inwestycja.nazwa if obj.inwestycja else "Brak inwestycji"

@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
    inlines = [InwestycjaZdjecieInline]
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
