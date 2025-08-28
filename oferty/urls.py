from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),          # strona główna
    path('oferty/', views.lista_ofert, name='lista_ofert'),  # tabela ofert
]
