"""
URLs para Funcionarios Web.
"""
from django.urls import path
from .views import funcionarios_list_view

app_name = 'funcionarios'

urlpatterns = [
    path('list/', funcionarios_list_view, name='list'),
]
