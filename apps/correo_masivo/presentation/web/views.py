"""
Views Web para Correo Masivo siguiendo arquitectura hexagonal.

Maneja las peticiones HTTP para el sistema de correo masivo.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
import json

from apps.correo_masivo.infrastructure.models import FirmaCorreo, PlantillaFirma, ListaRemitentes, FuncionarioEnLista
from apps.models import Funcionario
from django.db.models import Q, Count


class CorreoMasivoBaseView(LoginRequiredMixin, TemplateView):
    """Vista base para correo masivo."""
    pass


class ListaFuncionariosView(CorreoMasivoBaseView):
    """
    Vista para gestionar listas de remitentes de correo masivo.
    
    Permite crear, editar y gestionar listas de funcionarios para envío masivo.
    """
    template_name = "correo_masivo/lista_funcionarios.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener listas de remitentes del usuario actual
        listas_remitentes = ListaRemitentes.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_modificacion')
        
        # Paginación
        paginator = Paginator(listas_remitentes, 10)
        page = self.request.GET.get('page', 1)
        listas_paginadas = paginator.get_page(page)
        
        # Obtener funcionarios disponibles para agregar a listas
        # Forzamos el uso de postgres_db para evitar que el router
        # derive accidentalmente a SQLite (main)
        funcionarios_disponibles = Funcionario.objects.using('postgres_db').filter(
            estado='activo',
            eliminado=False
        ).order_by('apellidos', 'nombres')
        

        
        # Obtener unidad del usuario actual para nuevas listas
        unidad_usuario = getattr(self.request.user, 'unidad', 'Sin Unidad')
        if hasattr(unidad_usuario, 'nombre'):
            unidad_usuario = unidad_usuario.nombre
        
        context.update({
            'listas_remitentes': listas_paginadas,
            'funcionarios_disponibles': funcionarios_disponibles,
            'funcionarios_disponibles_count': funcionarios_disponibles.count(),  # Calcular aquí, no en template
            'unidad_usuario': unidad_usuario,
            'total_listas': listas_remitentes.count(),
        })
        
        return context
    
    def get(self, request, *args, **kwargs):
        """Manejar peticiones GET para AJAX"""
        action = request.GET.get('action')
        
        if action == 'ver_lista':
            # Ver funcionarios de una lista
            lista_id = request.GET.get('lista_id')
            try:
                lista = ListaRemitentes.objects.get(id=lista_id, usuario=request.user)
                funcionarios_en_lista = FuncionarioEnLista.objects.filter(
                    lista_remitentes=lista,
                    activo_en_lista=True
                )
                
                # Obtener IDs de funcionarios
                funcionarios_ids = funcionarios_en_lista.values_list('funcionario_id', flat=True)
                
                # Obtener datos de funcionarios desde PostgreSQL
                funcionarios_data = {}
                if funcionarios_ids:
                    from apps.models import Funcionario
                    funcionarios = Funcionario.objects.using('postgres_db').filter(id__in=funcionarios_ids)
                    funcionarios_data = {f.id: f for f in funcionarios}
                
                html = f"""
                <div class="mb-3">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0 me-3">
                            <div class="avatar-md">
                                <div class="avatar-title bg-success-subtle text-success rounded fs-18">
                                    <i class="ri-mail-send-line"></i>
                                </div>
                            </div>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="mb-1">{lista.nombre}</h5>
                            <p class="text-muted mb-0">{lista.descripcion or 'Sin descripción'}</p>
                            <small class="text-muted">
                                <i class="ri-user-line me-1"></i>{funcionarios_en_lista.count()} funcionarios
                                <span class="mx-2">|</span>
                                <i class="ri-building-line me-1"></i>{lista.unidad}
                            </small>
                        </div>
                    </div>
                </div>
                """
                
                if funcionarios_en_lista.exists():
                    html += """
                    <div class="table-responsive">
                        <table class="table table-borderless table-nowrap align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Funcionario</th>
                                    <th>Email</th>
                                    <th>Fecha Agregado</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    for func_en_lista in funcionarios_en_lista:
                        funcionario = funcionarios_data.get(func_en_lista.funcionario_id)
                        if not funcionario:  # Saltar si el funcionario no existe en PostgreSQL
                            continue
                        html += f"""
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="flex-shrink-0 me-2">
                                        <div class="avatar-xs">
                                            <div class="avatar-title bg-primary-subtle text-primary rounded-circle">
                                                {funcionario.nombres[0] if funcionario.nombres else '?'}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1">
                                        <h6 class="mb-0">{funcionario.apellidos}, {funcionario.nombres}</h6>
                                    </div>
                                </div>
                            </td>
                            <td>{funcionario.email or 'Sin email'}</td>
                            <td>{func_en_lista.fecha_agregado.strftime('%d/%m/%Y %H:%M')}</td>
                        </tr>
                        """
                    
                    html += """
                            </tbody>
                        </table>
                    </div>
                    """
                else:
                    html += """
                    <div class="text-center py-4">
                        <i class="ri-user-unfollow-line display-4 text-muted"></i>
                        <h5 class="mt-3">No hay funcionarios</h5>
                        <p class="text-muted">Esta lista no tiene funcionarios asignados.</p>
                    </div>
                    """
                
                return JsonResponse({
                    'success': True,
                    'html': html
                })
                
            except ListaRemitentes.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Lista no encontrada'
                })
        
        elif action == 'get_lista':
            # Obtener datos de una lista para edición
            lista_id = request.GET.get('lista_id')
            
            try:
                lista = ListaRemitentes.objects.get(id=lista_id, usuario=request.user)
                funcionarios_ids = list(FuncionarioEnLista.objects.filter(
                    lista_remitentes=lista,
                    activo_en_lista=True
                ).values_list('funcionario_id', flat=True))
                
                return JsonResponse({
                    'success': True,
                    'lista': {
                        'id': lista.id,
                        'nombre': lista.nombre,
                        'descripcion': lista.descripcion,
                        'funcionarios_ids': funcionarios_ids
                    }
                })
                
            except ListaRemitentes.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Lista no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error interno: {str(e)}'
                })
        
        # Si no es una petición AJAX, renderizar template normal
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Manejar peticiones POST para crear/editar listas de remitentes"""
        action = request.POST.get('action')
        
        if action == 'crear_lista':
            # Crear nueva lista de remitentes
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            funcionarios_ids = request.POST.getlist('funcionarios[]')
            
            if not nombre:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de la lista es requerido'
                })
            
            # Verificar que no exista una lista con el mismo nombre para este usuario
            if ListaRemitentes.objects.filter(usuario=request.user, nombre=nombre).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe una lista con este nombre'
                })
            
            try:
                # Obtener unidad del usuario
                unidad_usuario = getattr(request.user, 'unidad', 'Sin Unidad')
                if hasattr(unidad_usuario, 'nombre'):
                    unidad_usuario = unidad_usuario.nombre
                
                # Crear la lista
                lista = ListaRemitentes.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    usuario=request.user,
                    unidad=str(unidad_usuario)
                )
                
                # Agregar funcionarios a la lista
                if funcionarios_ids:
                    funcionarios = Funcionario.objects.using('postgres_db').filter(
                        id__in=funcionarios_ids,
                        estado='activo',
                        eliminado=False
                    )
                    
                    for funcionario in funcionarios:
                        FuncionarioEnLista.objects.create(
                            lista_remitentes=lista,
                            funcionario_id=funcionario.id,
                            agregado_por=request.user
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Lista "{nombre}" creada exitosamente',
                    'lista_id': lista.id
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear la lista: {str(e)}'
                })
        
        elif action == 'eliminar_lista':
            # Eliminar lista de remitentes
            lista_id = request.POST.get('lista_id')
            try:
                lista = ListaRemitentes.objects.get(id=lista_id, usuario=request.user)
                nombre_lista = lista.nombre
                lista.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Lista "{nombre_lista}" eliminada exitosamente'
                })
                
            except ListaRemitentes.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Lista no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al eliminar la lista: {str(e)}'
                })
        
        elif action == 'editar_lista':
            # Editar lista de remitentes
            lista_id = request.POST.get('lista_id')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            funcionarios_ids = request.POST.getlist('funcionarios[]')
            
            
            try:
                lista = ListaRemitentes.objects.get(id=lista_id, usuario=request.user)
                
                # Verificar nombre único (excepto la misma lista)
                if ListaRemitentes.objects.filter(usuario=request.user, nombre=nombre).exclude(id=lista.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'Ya existe una lista con este nombre'
                    })
                
                # Actualizar datos básicos
                lista.nombre = nombre
                lista.descripcion = descripcion
                lista.save()
                
                # Actualizar funcionarios
                # Eliminar relaciones existentes
                FuncionarioEnLista.objects.filter(lista_remitentes=lista).delete()
                
                # Agregar nuevos funcionarios
                if funcionarios_ids:
                    funcionarios = Funcionario.objects.using('postgres_db').filter(
                        id__in=funcionarios_ids,
                        estado='activo',
                        eliminado=False
                    )
                    
                    for funcionario in funcionarios:
                        FuncionarioEnLista.objects.create(
                            lista_remitentes=lista,
                            funcionario_id=funcionario.id,
                            agregado_por=request.user
                        )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Lista "{nombre}" actualizada exitosamente'
                })
                
            except ListaRemitentes.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Lista no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar la lista: {str(e)}'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Acción no reconocida'
        })


@method_decorator(csrf_exempt, name='dispatch')
class GestionarFirmaView(CorreoMasivoBaseView):
    """
    Vista para gestionar la firma de correos.
    
    Permite crear y editar firmas para incluir en los correos.
    """
    template_name = "correo_masivo/gestionar_firma.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener firma más reciente del usuario como referencia
        try:
            firma_actual = FirmaCorreo.objects.filter(
                usuario=self.request.user
            ).order_by('-fecha_modificacion').first()
        except FirmaCorreo.DoesNotExist:
            firma_actual = None
            
        context.update({
            'firma_actual': firma_actual,
            'plantillas': PlantillaFirma.objects.filter(activa=True)
        })
        
        return context
    
    def get(self, request, *args, **kwargs):
        """Manejar peticiones GET incluyendo AJAX"""
        action = request.GET.get('action')
        
        if action == 'get_firma':
            # Obtener datos de una firma específica
            firma_id = request.GET.get('id')
            try:
                firma = FirmaCorreo.objects.get(id=firma_id, usuario=request.user)
                return JsonResponse({
                    'success': True,
                    'firma': {
                        'id': firma.id,
                        'nombre_completo': firma.nombre_completo,
                        'cargo': firma.cargo,
                        'unidad': firma.unidad,
                        'institucion': firma.institucion,
                        'telefono': firma.telefono,
                        'email': firma.email,
                        'website': firma.website,
                        'color_principal': firma.color_principal,
                        'incluir_logos': firma.incluir_logos,
                        'logo_gobierno_url': firma.logo_gobierno.url if firma.logo_gobierno else None,
                        'logo_salud_url': firma.logo_salud.url if firma.logo_salud else None,
                        'logo_hospital_url': firma.logo_hospital.url if firma.logo_hospital else None,
                    }
                })
            except FirmaCorreo.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Firma no encontrada'
                }, status=404)
        
        elif action == 'preview_firma':
            # Obtener HTML de vista previa
            firma_id = request.GET.get('id')
            try:
                firma = FirmaCorreo.objects.get(id=firma_id, usuario=request.user)
                # Regenerar HTML para asegurar que los logos estén actualizados
                html_firma_actualizado = firma.generar_html_firma()
                return JsonResponse({
                    'success': True,
                    'html_firma': html_firma_actualizado,
                    'nombre': firma.nombre_completo,
                    'email': firma.email
                })
            except FirmaCorreo.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Firma no encontrada'
                }, status=404)
        
        elif action == 'get_user_signature':
            # Obtener firma más reciente del usuario para insertar en correos
            try:
                firma = FirmaCorreo.objects.filter(usuario=request.user).order_by('-fecha_modificacion').first()
                if firma:
                    html_firma_actualizado = firma.generar_html_firma()
                    return JsonResponse({
                        'success': True,
                        'html_firma': html_firma_actualizado
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'No se encontró firma configurada'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al obtener firma: {str(e)}'
                }, status=500)
        
        # Si no es una petición AJAX, renderizar template normal
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Manejar diferentes acciones via AJAX"""
        try:
            # Determinar la acción
            if request.content_type == 'application/json':
                # Peticiones JSON para acciones especiales
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'delete':
                    # Eliminar firma
                    firma_id = data.get('firma_id')
                    try:
                        firma = FirmaCorreo.objects.get(id=firma_id, usuario=request.user)
                        firma.delete()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Firma eliminada correctamente'
                        })
                    except FirmaCorreo.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'Firma no encontrada'
                        }, status=404)
            
            else:
                # Petición de formulario normal (crear/actualizar firma)
                action = request.POST.get('action', 'create')
                firma_id = request.POST.get('firma_id')
                
                # Extraer datos del formulario
                data = {
                    'nombre': request.POST.get('nombre', ''),
                    'cargo': request.POST.get('cargo', ''),
                    'unidad': request.POST.get('unidad', ''),
                    'institucion': request.POST.get('institucion', ''),
                    'telefono': request.POST.get('telefono', ''),
                    'email': request.POST.get('email', ''),
                    'website': request.POST.get('website', ''),
                    'plantilla': request.POST.get('plantilla', 'hospital'),
                    'color_principal': request.POST.get('color_principal', '#0066cc'),
                    'incluir_logos': request.POST.get('incluir_logos', 'true') == 'true',
                }
                
                # Extraer archivos de logos
                logos = {
                    'logo_gobierno': request.FILES.get('logo_gobierno'),
                    'logo_salud': request.FILES.get('logo_salud'),
                    'logo_hospital': request.FILES.get('logo_hospital'),
                }
                
                if action == 'update' and firma_id:
                    # Actualizar firma existente
                    try:
                        firma = FirmaCorreo.objects.get(id=firma_id, usuario=request.user)
                        
                        # Actualizar datos
                        firma.nombre_completo = data.get('nombre', '')
                        firma.cargo = data.get('cargo', '')
                        firma.unidad = data.get('unidad', '')
                        firma.institucion = data.get('institucion', '')
                        firma.telefono = data.get('telefono', '')
                        firma.email = data.get('email', '')
                        firma.website = data.get('website', '')
                        firma.plantilla = data.get('plantilla', 'hospital')
                        firma.color_principal = data.get('color_principal', '#0066cc')
                        firma.incluir_logos = data.get('incluir_logos', True)
                        
                        # Actualizar logos si se proporcionaron nuevos archivos
                        for logo_field, logo_file in logos.items():
                            if logo_file:
                                setattr(firma, logo_field, logo_file)
                        
                        # Generar HTML de la firma
                        firma.generar_html_firma()
                        firma.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Firma actualizada correctamente',
                            'firma_id': firma.id,
                            'html_firma': firma.html_firma
                        })
                        
                    except FirmaCorreo.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'Firma no encontrada'
                        }, status=404)
                
                else:
                    # Crear nueva firma
                    firma = FirmaCorreo.objects.create(
                        usuario=request.user,
                        nombre_completo=data.get('nombre', ''),
                        cargo=data.get('cargo', ''),
                        unidad=data.get('unidad', ''),
                        institucion=data.get('institucion', ''),
                        telefono=data.get('telefono', ''),
                        email=data.get('email', ''),
                        website=data.get('website', ''),
                        plantilla=data.get('plantilla', 'hospital'),
                        color_principal=data.get('color_principal', '#0066cc'),
                        incluir_logos=data.get('incluir_logos', True),
                        es_predeterminada=False,  # Todas las firmas son iguales
                    )
                    
                    # Agregar logos si se proporcionaron
                    for logo_field, logo_file in logos.items():
                        if logo_file:
                            setattr(firma, logo_field, logo_file)
                    
                    # Generar HTML de la firma
                    firma.generar_html_firma()
                    firma.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Firma creada correctamente',
                        'firma_id': firma.id,
                        'html_firma': firma.html_firma
                    })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)


class EnviarCorreoView(CorreoMasivoBaseView):
    """
    Vista para crear y enviar correos masivos.
    
    Permite componer correos, seleccionar destinatarios y programar envíos.
    """
    template_name = "correo_masivo/enviar_correo.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Destinatarios disponibles (funcionarios)
        funcionarios_disponibles = Funcionario.objects.using('postgres_db').filter(
            estado='activo',
            eliminado=False
        ).order_by('apellidos', 'nombres')
        
        # Obtener listas de remitentes del usuario para selección
        listas_remitentes = ListaRemitentes.objects.filter(
            usuario=self.request.user,
            activa=True
        ).annotate(
            total_funcionarios=Count('funcionarios')
        ).order_by('nombre')
        
        context.update({
            'funcionarios_disponibles': funcionarios_disponibles,
            'listas_remitentes': listas_remitentes,
            'usuario_nombre': self.request.user.get_full_name() or self.request.user.username,
            'usuario_email': self.request.user.email
        })
        
        return context
    
    def post(self, request):
        """Maneja el envío de correos masivos."""
        # Extraer datos del formulario
        data = {
            'asunto': request.POST.get('asunto', '').strip(),
            'contenido': request.POST.get('contenido', '').strip(),
            'destinatarios': request.POST.getlist('destinatarios'),
            'programar': request.POST.get('programar') == 'true',
            'fecha_programada': request.POST.get('fecha_programada', ''),
            'hora_programada': request.POST.get('hora_programada', '')
        }
        
        # Validaciones básicas
        errores = []
        if not data['asunto']:
            errores.append('El asunto es requerido')
        if not data['contenido']:
            errores.append('El contenido es requerido')
        if not data['destinatarios']:
            errores.append('Debe seleccionar al menos un destinatario')
        
        if data['programar']:
            if not data['fecha_programada']:
                errores.append('La fecha programada es requerida')
            if not data['hora_programada']:
                errores.append('La hora programada es requerida')
        
        if errores:
            return JsonResponse({
                'success': False,
                'errors': errores
            }, status=400)
        
        # TODO: Aquí iría la lógica para crear y enviar/programar el correo
        # Por ahora solo simulamos éxito
        
        tipo_envio = "programado" if data['programar'] else "inmediato"
        mensaje = f"Correo {tipo_envio} exitosamente para {len(data['destinatarios'])} destinatarios"
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'correo_id': 123  # Mock ID
        })


# Exportar views para URLs
lista_funcionarios_view = ListaFuncionariosView.as_view()
gestionar_firma_view = GestionarFirmaView.as_view()
enviar_correo_view = EnviarCorreoView.as_view()
