from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import LogAuditoria, UsuarioSistema
import socket

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Obtener la IP real del cliente, incluso en desarrollo local
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')

    # Si estamos en localhost, intentar obtener la IP real del equipo
    if ip in ('127.0.0.1', 'localhost', '::1') or not ip:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip and local_ip not in ('127.0.0.1', 'localhost', '::1'):
                ip = local_ip
        except Exception:
            pass

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    LogAuditoria.objects.create(
        usuario=user,
        accion='LOGIN',
        entidad='UsuarioSistema',
        entidad_id=user.id,
        descripcion=f"Usuario {user.username} inició sesión.",
        valores_previos=None,
        valores_nuevos=None,
        ip_usuario=ip,
        user_agent=user_agent,
        created_at=timezone.now()
    )
