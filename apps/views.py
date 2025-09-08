from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .models import Funcionario

# Create your views here.

class AppsView(LoginRequiredMixin,TemplateView):
    pass

calendar_view = AppsView.as_view(template_name="apps/apps-calendar.html")

# chat
chat_view = AppsView.as_view(template_name="apps/chat/apps-chat.html")
chat_video_conference_chat_view = AppsView.as_view(template_name="apps/chat/apps-chat-video-conference.html")

# crypto
crypto_marketplace_view = AppsView.as_view(template_name="apps/crypto/apps-crypto-marketplace.html")
crypto_exchange_view = AppsView.as_view(template_name="apps/crypto/apps-crypto-exchange.html")
crypto_ico_view = AppsView.as_view(template_name="apps/crypto/apps-crypto-ico.html")
crypto_transactions_view = AppsView.as_view(template_name="apps/crypto/apps-crypto-transactions.html")
crypto_coin_overview_view = AppsView.as_view(template_name="apps/crypto/apps-crypto-coin-overview.html")

# customers
customers_list_view = AppsView.as_view(template_name="apps/customers/apps-customers-list.html")
customers_overview_view = AppsView.as_view(template_name="apps/customers/apps-customers-overview.html")

file_manager_view = AppsView.as_view(template_name="apps/apps-file-manager.html")

# invoices
invoices_list_view = AppsView.as_view(template_name="apps/invoices/apps-invoices-list.html")
invoices_create_view = AppsView.as_view(template_name="apps/invoices/apps-invoices-create.html")
invoices_overview_view = AppsView.as_view(template_name="apps/invoices/apps-invoices-overview.html")

notes_view = AppsView.as_view(template_name="apps/apps-notes.html")

to_do_view = AppsView.as_view(template_name="apps/apps-to-do.html")

# forms
form_perfil_view = AppsView.as_view(template_name="apps/forms/form-perfil.html")

# funcionarios
class FuncionariosListView(LoginRequiredMixin, ListView):
    model = Funcionario
    template_name = "apps/funcionarios/apps-funcionarios-list.html"
    context_object_name = 'funcionarios'
    paginate_by = 10
    
    def get_queryset(self):
        # Usar la base de datos de funcionarios específicamente
        queryset = Funcionario.objects.using('postgres_db').filter(eliminado=False)
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(nombres__icontains=search) |
                models.Q(apellidos__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        return queryset.order_by('apellidos', 'nombres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para los cards (usando la DB correcta y excluyendo eliminados)
        funcionarios_activos_db = Funcionario.objects.using('postgres_db').filter(eliminado=False)
        context['total_funcionarios'] = funcionarios_activos_db.count()
        context['funcionarios_activos'] = funcionarios_activos_db.filter(estado='activo').count()
        context['funcionarios_inactivos'] = funcionarios_activos_db.filter(estado='inactivo').count()
        
        # Filtros actuales para mantener en la paginación
        context['current_search'] = self.request.GET.get('search', '')
        context['current_estado'] = self.request.GET.get('estado', '')
        
        return context

funcionarios_list_view = FuncionariosListView.as_view()
