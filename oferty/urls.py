from django.urls import path
from . import views

urlpatterns = [
    path("inwestycja/<int:pk>/", views.szczegoly_inwestycji, name="szczegoly_inwestycji"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)