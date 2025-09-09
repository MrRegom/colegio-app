"""
URL configuration for judia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from .views import MyPasswordChangeView, MyPasswordSetView

from core.views import (
    
    dashboard_view,
    dashboard_analytics_view,
    dashboard_crypto_view,
)

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    # dashboard
    path('',view=dashboard_view,name='dashboard'),
    path('dashboard_analytics',view=dashboard_analytics_view,name='dashboard_analytics'),
    path('dashboard_crypto',view=dashboard_crypto_view,name='dashboard_crypto'),
    

    # apps
    path('apps/',include('apps.urls')),
    
    path('pages/',include('apps.pages.presentation.web.urls')),
    
    # components
    path('components/',include('components.urls')),
    
    # contacto
    path('contacto/', include('contacto.urls')),

    # correo masivo
    path('correo_masivo/',include('apps.correo_masivo.presentation.web.urls')),

    # solicitudes_perfil
    path('solicitudes-perfil/', include('solicitudes_perfil.urls')),
    
    

    # water (temporalmente deshabilitada)
    # path('water/',include('water.urls')),
    
    # medicals_systems (temporalmente deshabilitada)
    # path('medicals_systems/',include('medicals_systems.urls')),
    
    path(
        "account/password/change/",
        login_required(MyPasswordChangeView.as_view()),
        name="account_change_password",
    ),
    path(
        "account/password/set/",
        login_required(MyPasswordSetView.as_view()),
        name="account_set_password",
    ),
    
    # All Auth 
    path('account/', include('allauth.urls')),
    
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir archivos estáticos
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
