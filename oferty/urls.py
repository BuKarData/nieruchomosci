from django.urls import path
from . import views

app_name = "oferty"

urlpatterns = [
    path("", views.home, name="home"),          # strona główna inwestycji
    path("oferty/", views.lista_ofert, name="lista_ofert"),  # pełna lista ofert
]
