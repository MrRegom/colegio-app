from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notificacion, TipoNotificacion, ConfiguracionNotificacion


@login_required
def lista_notificaciones(request):
    """Vista para listar notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(
        usuario_destino=request.user,
        archivada=False
    ).select_related('tipo', 'usuario_origen').order_by('-fecha_creacion')

    # Filtros
    solo_no_leidas = request.GET.get('no_leidas')
    if solo_no_leidas:
        notificaciones = notificaciones.filter(leida=False)

    # Contar no leídas
    no_leidas = Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False,
        archivada=False
    ).count()

    context = {
        'notificaciones': notificaciones,
        'no_leidas': no_leidas,
        'titulo': 'Notificaciones'
    }
    return render(request, 'notificaciones/lista_notificaciones.html', context)


@login_required
def marcar_como_leida(request, pk):
    """Vista para marcar una notificación como leída"""
    notificacion = get_object_or_404(
        Notificacion,
        pk=pk,
        usuario_destino=request.user
    )
    notificacion.marcar_como_leida()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notificaciones:lista_notificaciones')


@login_required
def marcar_todas_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False
    ).update(leida=True, fecha_lectura=timezone.now())

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notificaciones:lista_notificaciones')


@login_required
def archivar_notificacion(request, pk):
    """Vista para archivar una notificación"""
    notificacion = get_object_or_404(
        Notificacion,
        pk=pk,
        usuario_destino=request.user
    )
    notificacion.archivada = True
    notificacion.save(update_fields=['archivada'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notificaciones:lista_notificaciones')


@login_required
def configuracion_notificaciones(request):
    """Vista para configurar preferencias de notificaciones"""
    tipos = TipoNotificacion.objects.filter(activo=True)

    # Obtener o crear configuraciones
    configuraciones = []
    for tipo in tipos:
        config, created = ConfiguracionNotificacion.objects.get_or_create(
            usuario=request.user,
            tipo_notificacion=tipo,
            defaults={
                'notificacion_sistema': True,
                'notificacion_email': tipo.enviar_email
            }
        )
        configuraciones.append(config)

    if request.method == 'POST':
        # Actualizar configuraciones
        for config in configuraciones:
            sistema_key = f'sistema_{config.tipo_notificacion.id}'
            email_key = f'email_{config.tipo_notificacion.id}'

            config.notificacion_sistema = sistema_key in request.POST
            config.notificacion_email = email_key in request.POST
            config.save()

        return redirect('notificaciones:configuracion')

    context = {
        'configuraciones': configuraciones,
        'titulo': 'Configuración de Notificaciones'
    }
    return render(request, 'notificaciones/configuracion.html', context)


@login_required
def contador_notificaciones(request):
    """Vista AJAX para obtener el contador de notificaciones no leídas"""
    contador = Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False,
        archivada=False
    ).count()

    return JsonResponse({'contador': contador})
