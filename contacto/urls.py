from django.urls import path
from .views import (
    ContactoCreateView, ContactoListView, ContactoUpdateView, ContactoDeleteView
)

urlpatterns = [
    path('', ContactoListView.as_view(), name='contacto_list'),
    path('nuevo/', ContactoCreateView.as_view(), name='contacto_nuevo'),
    path('editar/<int:pk>/', ContactoUpdateView.as_view(), name='contacto_editar'),
    path('eliminar/<int:pk>/', ContactoDeleteView.as_view(), name='contacto_eliminar'),
]