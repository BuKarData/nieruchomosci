from django.contrib import admin
from django.urls import path, include
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .views import home, lista_ofert
from .api import data_api_view, metadata_xml

urlpatterns = [
    path('', home, name='home'),
    path('oferty/', lista_ofert, name='lista_ofert'),
    path('api/data.jsonld', data_api_view, name='data-jsonld'),
    path('api/data.csv', data_api_view, name='data-csv'),
    path('api/data.xlsx', data_api_view, name='data-xlsx'),
    path('api/metadata.xml', metadata_xml, name='metadata-xml'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)