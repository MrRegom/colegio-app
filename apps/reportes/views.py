from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import TipoReporte, ReporteGenerado, MovimientoInventario
from apps.activos.models import MovimientoActivo, UbicacionActual, Activo


@login_required
def lista_reportes(request):
    """Vista para listar tipos de reportes disponibles"""
    tipos_reportes = TipoReporte.objects.filter(activo=True).order_by('modulo', 'codigo')

    context = {
        'tipos_reportes': tipos_reportes,
        'titulo': 'Reportes Disponibles'
    }
    return render(request, 'reportes/lista_reportes.html', context)


@login_required
def historial_reportes(request):
    """Vista para ver el historial de reportes generados"""
    reportes = ReporteGenerado.objects.select_related(
        'tipo_reporte', 'usuario'
    ).order_by('-fecha_generacion')[:100]

    context = {
        'reportes': reportes,
        'titulo': 'Historial de Reportes'
    }
    return render(request, 'reportes/historial_reportes.html', context)


@login_required
def reporte_inventario_actual(request):
    """Vista para ver el reporte de ubicación actual de activos"""
    ubicaciones = UbicacionActual.objects.select_related(
        'activo', 'ubicacion', 'responsable', 'activo__categoria', 'activo__estado'
    ).all()

    # Estadísticas
    total_items = ubicaciones.count()
    total_activos = Activo.objects.filter(activo=True).count()
    total_valor = Activo.objects.filter(activo=True).aggregate(
        total=Sum('precio_unitario')
    )['total'] or 0

    context = {
        'ubicaciones': ubicaciones,
        'total_items': total_items,
        'total_activos': total_activos,
        'total_valor': total_valor,
        'titulo': 'Ubicación Actual de Activos'
    }
    return render(request, 'reportes/inventario_actual.html', context)


@login_required
def reporte_movimientos(request):
    """Vista para ver el reporte de movimientos de inventario"""
    # Por defecto, últimos 30 días
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if not fecha_desde:
        fecha_desde = timezone.now() - timedelta(days=30)
    if not fecha_hasta:
        fecha_hasta = timezone.now()

    movimientos = MovimientoInventario.objects.select_related(
        'activo', 'bodega_origen', 'bodega_destino', 'usuario'
    ).filter(
        fecha_movimiento__gte=fecha_desde,
        fecha_movimiento__lte=fecha_hasta
    )

    # Estadísticas por tipo
    stats_tipo = movimientos.values('tipo_movimiento').annotate(
        total=Count('id')
    ).order_by('-total')

    context = {
        'movimientos': movimientos,
        'stats_tipo': stats_tipo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'titulo': 'Movimientos de Inventario'
    }
    return render(request, 'reportes/movimientos.html', context)


@login_required
def dashboard_reportes(request):
    """Vista para el dashboard de reportes con estadísticas generales"""
    # Movimientos del último mes
    fecha_inicio = timezone.now() - timedelta(days=30)
    movimientos_mes = MovimientoInventario.objects.filter(
        fecha_movimiento__gte=fecha_inicio
    )

    stats = {
        'total_movimientos': movimientos_mes.count(),
        'entradas': movimientos_mes.filter(tipo_movimiento='ENTRADA').count(),
        'salidas': movimientos_mes.filter(tipo_movimiento='SALIDA').count(),
        'traspasos': movimientos_mes.filter(tipo_movimiento='TRASPASO').count(),
    }

    # Total de activos
    total_activos = Activo.objects.filter(activo=True).count()
    activos_asignados = UbicacionActual.objects.filter(
        ubicacion__isnull=False
    ).count()

    # Reportes recientes
    reportes_recientes = ReporteGenerado.objects.select_related(
        'tipo_reporte', 'usuario'
    ).order_by('-fecha_generacion')[:10]

    context = {
        'stats': stats,
        'total_activos': total_activos,
        'activos_asignados': activos_asignados,
        'reportes_recientes': reportes_recientes,
        'titulo': 'Dashboard de Reportes'
    }
    return render(request, 'reportes/dashboard.html', context)
