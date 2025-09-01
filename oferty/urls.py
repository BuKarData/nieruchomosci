from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ofert, name="lista_ofert"),
    path('dodaj/', views.dodaj_oferte, name="dodaj_oferte"),
    path('<int:oferta_id>/cena/', views.dodaj_cene, name="dodaj_cene"),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)