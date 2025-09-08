from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Contacto
from .forms import ContactoForm

class ContactoCreateView(CreateView):
    model = Contacto
    form_class = ContactoForm
    template_name = "contacto/contacto_form.html"
    success_url = reverse_lazy('contacto_list')

class ContactoListView(ListView):
    model = Contacto
    template_name = "contacto/contacto_list.html"
    context_object_name = "contactos"

class ContactoUpdateView(UpdateView):
    model = Contacto
    form_class = ContactoForm
    template_name = "contacto/contacto_form.html"
    success_url = reverse_lazy('contacto_list')

class ContactoDeleteView(DeleteView):
    model = Contacto
    template_name = "contacto/contacto_confirm_delete.html"
    success_url = reverse_lazy('contacto_list')
