from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from allauth.account.views import PasswordChangeView, PasswordSetView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    pass

dashboard_view = DashboardView.as_view(template_name="index.html")
dashboard_analytics_view = DashboardView.as_view(template_name="dashboard-analytics.html")
dashboard_crypto_view = DashboardView.as_view(template_name="dashboard-crypto.html")


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy("dashboard")


class MyPasswordSetView(LoginRequiredMixin, PasswordSetView):
    success_url = reverse_lazy("dashboard")