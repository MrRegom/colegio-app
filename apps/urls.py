from django.urls import path
from apps.views_hexagonal import (
    
    
    calendar_view,
    
    # chat
    chat_view,
    chat_video_conference_chat_view,
    
    # crypto
    crypto_marketplace_view,
    crypto_exchange_view,
    crypto_ico_view,
    crypto_transactions_view,
    crypto_coin_overview_view,
    
    # customers
    customers_list_view,
    customers_overview_view,
    
    file_manager_view,
    
    # invoices
    invoices_list_view,
    invoices_create_view,
    invoices_overview_view,
    
    notes_view,

    to_do_view,
    
    # forms
    form_perfil_view,
    
    # funcionarios - ARQUITECTURA HEXAGONAL
    funcionarios_list_view,
)

app_name = 'apps'

urlpatterns = [
    
    path('calendar',view=calendar_view,name='calendar'),
    
    
    # chat
    path('chat/chat_view',view=chat_view,name='chat.chat_view'),
    path('chat/video_conference_chat',view=chat_video_conference_chat_view,name='chat.video_conference_chat'),
    
    # crypto
    path('crypto/marketplace',view=crypto_marketplace_view,name='crypto.marketplace'),
    path('crypto/exchange',view=crypto_exchange_view,name='crypto.exchange'),
    path('crypto/ico',view=crypto_ico_view,name='crypto.ico'),
    path('crypto/transactions',view=crypto_transactions_view,name='crypto.transactions'),
    path('crypto/coin_overview',view=crypto_coin_overview_view,name='crypto.coin_overview'),
    
    # customers
    path('customers/list',view=customers_list_view,name='customers.list'),
    path('customers/overview',view=customers_overview_view,name='customers.overview'),
    
    path('file_manager',view=file_manager_view,name='file_manager'),

    
    # invoices
    path('invoices/invoices_list',view=invoices_list_view,name='invoices.invoices_list'),
    path('invoices/invoice_create',view=invoices_create_view,name='invoices.invoice_create'),
    path('invoices/invoice_overview',view=invoices_overview_view,name='invoices.invoice_overview'),

    path('notes',view=notes_view,name='notes'),
    
    path('to_do',view=to_do_view,name='to_do'),
    
    # forms
    path('forms/form-perfil',view=form_perfil_view,name='forms.form_perfil'),
    
    # funcionarios
    path('funcionarios/list',view=funcionarios_list_view,name='funcionarios.list'),
]