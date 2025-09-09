from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import LogAuditoria, UsuarioSistema

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    LogAuditoria.objects.create(
        usuario=user,
        accion='LOGIN',
        entidad='UsuarioSistema',
        entidad_id=user.id,
        descripcion=f"Usuario {user.username} inició sesión.",
        valores_previos=None,
        valores_nuevos=None,
        ip_remota=ip,
        user_agent=user_agent,
        created_at=timezone.now()
    )
