"""
Servicios de Dominio para Accounts.

Contiene la lógica de negocio pura que no pertenece
a una entidad específica pero es parte del dominio.
"""
from typing import List, Optional
from datetime import datetime, timedelta

from .entities import (
    UsuarioSistema, 
    Unidad, 
    EventoAuditoria,
    Email,
    NombreCompleto,
    RolUsuario,
    EstadoUsuario,
    TipoAccion
)
from .repositories import IUsuarioSistemaRepository, IUnidadRepository, IAuditoriaRepository


class PermisosService:
    """
    Servicio de dominio para gestión de permisos.
    
    Centraliza la lógica de negocio relacionada con permisos y autorizaciones.
    """
    
    # Permisos del sistema
    PERMISOS_DISPONIBLES = [
        "can_manage_unit_users",      # Gestionar usuarios de su unidad
        "can_view_unit_reports",      # Ver reportes de su unidad
        "can_create_mass_emails",     # Crear envíos masivos de correo
        "can_manage_email_lists",     # Gestionar listas de correo
        "can_view_email_analytics",   # Ver analíticas de envíos
        "can_manage_email_templates", # Gestionar plantillas de correo
        "can_manage_all_users",       # Gestionar todos los usuarios (super admin)
        "can_manage_units",           # Gestionar unidades
        "can_view_audit_logs",        # Ver logs de auditoría
    ]

    # Permisos por rol por defecto
    PERMISOS_POR_ROL = {
        RolUsuario.ADMIN: [
            "can_manage_unit_users",
            "can_view_unit_reports", 
            "can_create_mass_emails",
            "can_manage_email_lists",
            "can_view_email_analytics",
            "can_manage_email_templates",
            "can_manage_all_users",
            "can_manage_units",
            "can_view_audit_logs",
        ],
        RolUsuario.USUARIO: [
            "can_create_mass_emails",
            "can_manage_email_lists",
            "can_view_email_analytics",
        ]
    }

    @classmethod
    def get_permisos_por_rol(cls, rol: RolUsuario) -> List[str]:
        """Obtiene los permisos por defecto según el rol."""
        return cls.PERMISOS_POR_ROL.get(rol, [])

    @classmethod
    def es_permiso_valido(cls, permiso: str) -> bool:
        """Verifica si un permiso es válido."""
        return permiso in cls.PERMISOS_DISPONIBLES

    @classmethod
    def puede_gestionar_usuario(cls, gestor: UsuarioSistema, usuario_objetivo: UsuarioSistema) -> bool:
        """
        Verifica si un usuario puede gestionar a otro usuario.
        
        Reglas de negocio:
        - Los admins pueden gestionar usuarios de su unidad
        - Los super admins pueden gestionar cualquier usuario
        - Los usuarios normales no pueden gestionar otros usuarios
        """
        if not gestor.is_active:
            return False
            
        # Super admin puede gestionar cualquiera
        if gestor.tiene_permiso("can_manage_all_users"):
            return True
            
        # Admin de unidad puede gestionar usuarios de su unidad
        if (gestor.tiene_permiso("can_manage_unit_users") and 
            gestor.unidad_id == usuario_objetivo.unidad_id):
            return True
            
        return False

    @classmethod
    def puede_ver_datos_unidad(cls, usuario: UsuarioSistema, unidad_id: int) -> bool:
        """
        Verifica si un usuario puede ver datos de una unidad.
        
        Reglas de negocio:
        - Puede ver datos de su propia unidad
        - Los super admins pueden ver datos de cualquier unidad
        """
        if not usuario.is_active:
            return False
            
        # Super admin puede ver cualquier unidad
        if usuario.tiene_permiso("can_manage_all_users"):
            return True
            
        # Puede ver su propia unidad
        return usuario.unidad_id == unidad_id


class UsuarioService:
    """
    Servicio de dominio para operaciones complejas de usuarios.
    
    Maneja lógica de negocio que requiere múltiples entidades.
    """

    def __init__(self, usuario_repo: IUsuarioSistemaRepository, 
                 unidad_repo: IUnidadRepository,
                 auditoria_repo: IAuditoriaRepository):
        self._usuario_repo = usuario_repo
        self._unidad_repo = unidad_repo
        self._auditoria_repo = auditoria_repo

    def crear_usuario_completo(self, username: str, email: str, nombres: str, 
                             apellidos: str, unidad_id: int, rol: RolUsuario,
                             creado_por_id: int) -> UsuarioSistema:
        """
        Crea un usuario completo con validaciones y auditoría.
        
        Incluye todas las validaciones de negocio y registro de auditoría.
        """
        # Validar que la unidad existe y está activa
        unidad = self._unidad_repo.get_by_id(unidad_id)
        if not unidad:
            raise ValueError(f"No existe la unidad con ID {unidad_id}")
        
        if not unidad.is_active:
            raise ValueError(f"La unidad '{unidad.nombre}' no está activa")

        # Validar unicidad
        email_obj = Email(email)
        if self._usuario_repo.exists_by_username(username):
            raise ValueError(f"Ya existe un usuario con username '{username}'")
        
        if self._usuario_repo.exists_by_email(email_obj):
            raise ValueError(f"Ya existe un usuario con email '{email}'")

        # Crear usuario
        nombre_completo = NombreCompleto(nombres, apellidos)
        usuario = UsuarioSistema(
            id=None,
            username=username,
            email=email_obj,
            nombre_completo=nombre_completo,
            unidad_id=unidad_id,
            rol=rol,
            estado=EstadoUsuario.ACTIVO,
            permisos_especiales=PermisosService.get_permisos_por_rol(rol)
        )

        # Guardar usuario
        usuario_creado = self._usuario_repo.save(usuario)

        # Registrar auditoría
        evento = EventoAuditoria.crear_evento_usuario(
            usuario_id=creado_por_id,
            accion=TipoAccion.CREAR_USUARIO,
            usuario_afectado_id=usuario_creado.id,
            descripcion=f"Usuario '{username}' creado en unidad '{unidad.nombre}'",
            valores_nuevos={
                "username": username,
                "email": email,
                "unidad_id": unidad_id,
                "rol": rol.value
            }
        )
        self._auditoria_repo.save(evento)

        return usuario_creado

    def cambiar_unidad_usuario(self, usuario_id: int, nueva_unidad_id: int, 
                              cambiado_por_id: int) -> UsuarioSistema:
        """
        Cambia la unidad de un usuario con validaciones y auditoría.
        """
        # Obtener usuario actual
        usuario = self._usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise ValueError(f"No existe usuario con ID {usuario_id}")

        # Validar nueva unidad
        nueva_unidad = self._unidad_repo.get_by_id(nueva_unidad_id)
        if not nueva_unidad:
            raise ValueError(f"No existe unidad con ID {nueva_unidad_id}")
        
        if not nueva_unidad.is_active:
            raise ValueError(f"La unidad '{nueva_unidad.nombre}' no está activa")

        # Obtener unidad anterior para auditoría
        unidad_anterior = self._unidad_repo.get_by_id(usuario.unidad_id)
        
        # Realizar cambio
        usuario.asignar_unidad(nueva_unidad_id)
        usuario_actualizado = self._usuario_repo.save(usuario)

        # Registrar auditoría
        evento = EventoAuditoria.crear_evento_usuario(
            usuario_id=cambiado_por_id,
            accion=TipoAccion.ACTUALIZAR_USUARIO,
            usuario_afectado_id=usuario_id,
            descripcion=f"Usuario '{usuario.username}' cambiado de '{unidad_anterior.nombre}' a '{nueva_unidad.nombre}'",
            valores_previos={"unidad_id": unidad_anterior.id, "unidad_nombre": unidad_anterior.nombre},
            valores_nuevos={"unidad_id": nueva_unidad_id, "unidad_nombre": nueva_unidad.nombre}
        )
        self._auditoria_repo.save(evento)

        return usuario_actualizado

    def obtener_estadisticas_unidad(self, unidad_id: int) -> dict:
        """
        Obtiene estadísticas completas de una unidad.
        """
        unidad = self._unidad_repo.get_by_id(unidad_id)
        if not unidad:
            raise ValueError(f"No existe unidad con ID {unidad_id}")

        usuarios_unidad = self._usuario_repo.get_by_unidad(unidad_id)
        usuarios_activos = [u for u in usuarios_unidad if u.is_active]
        administradores = [u for u in usuarios_unidad if u.is_admin]

        return {
            "unidad": {
                "id": unidad.id,
                "nombre": unidad.nombre,
                "estado": unidad.estado.value,
                "is_active": unidad.is_active
            },
            "usuarios": {
                "total": len(usuarios_unidad),
                "activos": len(usuarios_activos),
                "inactivos": len(usuarios_unidad) - len(usuarios_activos),
                "administradores": len(administradores)
            },
            "actividad_reciente": self._obtener_actividad_reciente_unidad(unidad_id)
        }

    def _obtener_actividad_reciente_unidad(self, unidad_id: int) -> dict:
        """Obtiene actividad reciente de usuarios de una unidad."""
        usuarios_unidad = self._usuario_repo.get_by_unidad(unidad_id)
        usuarios_ids = [u.id for u in usuarios_unidad if u.id]
        
        # Obtener eventos recientes de usuarios de la unidad
        eventos_recientes = []
        for user_id in usuarios_ids:
            eventos_usuario = self._auditoria_repo.get_by_usuario(user_id, limit=5)
            eventos_recientes.extend(eventos_usuario)
        
        # Ordenar por fecha y tomar los más recientes
        eventos_recientes.sort(key=lambda e: e.created_at or datetime.min, reverse=True)
        eventos_recientes = eventos_recientes[:10]

        return {
            "eventos_recientes": len(eventos_recientes),
            "ultimo_login": self._obtener_ultimo_login_unidad(usuarios_ids),
            "usuarios_activos_hoy": self._contar_usuarios_activos_hoy(usuarios_ids)
        }

    def _obtener_ultimo_login_unidad(self, usuarios_ids: List[int]) -> Optional[datetime]:
        """Obtiene la fecha del último login en la unidad."""
        ultimo_login = None
        
        for user_id in usuarios_ids:
            eventos_login = self._auditoria_repo.get_by_accion(TipoAccion.LOGIN, limit=1)
            eventos_usuario = [e for e in eventos_login if e.usuario_id == user_id]
            
            if eventos_usuario and eventos_usuario[0].created_at:
                if not ultimo_login or eventos_usuario[0].created_at > ultimo_login:
                    ultimo_login = eventos_usuario[0].created_at
        
        return ultimo_login

    def _contar_usuarios_activos_hoy(self, usuarios_ids: List[int]) -> int:
        """Cuenta usuarios que han tenido actividad hoy."""
        hoy = datetime.now().date()
        usuarios_activos = set()
        
        for user_id in usuarios_ids:
            eventos_usuario = self._auditoria_repo.get_by_usuario(user_id, limit=20)
            for evento in eventos_usuario:
                if (evento.created_at and 
                    evento.created_at.date() == hoy):
                    usuarios_activos.add(user_id)
                    break
        
        return len(usuarios_activos)


class AuditoriaService:
    """
    Servicio de dominio para operaciones de auditoría.
    
    Maneja la lógica de negocio relacionada con auditoría y compliance.
    """

    def __init__(self, auditoria_repo: IAuditoriaRepository):
        self._auditoria_repo = auditoria_repo

    def registrar_login(self, usuario_id: int, ip_remota: str, user_agent: str) -> EventoAuditoria:
        """Registra un evento de login."""
        evento = EventoAuditoria.crear_evento_login(usuario_id, ip_remota, user_agent)
        return self._auditoria_repo.save(evento)

    def obtener_reporte_actividad(self, desde: datetime, hasta: datetime) -> dict:
        """
        Genera un reporte completo de actividad del sistema.
        """
        eventos_criticos = self._auditoria_repo.get_eventos_criticos(desde, hasta)
        
        # Contar eventos por tipo
        contadores = {}
        for accion in TipoAccion:
            contadores[accion.value] = self._auditoria_repo.count_by_accion(accion, desde, hasta)

        return {
            "periodo": {
                "desde": desde.isoformat(),
                "hasta": hasta.isoformat()
            },
            "eventos_criticos": len(eventos_criticos),
            "contadores_por_accion": contadores,
            "eventos_criticos_detalle": [
                {
                    "accion": e.accion.value,
                    "descripcion": e.descripcion,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                } for e in eventos_criticos[:10]  # Top 10
            ]
        }

    def limpiar_logs_antiguos(self, dias_retencion: int = 365) -> int:
        """
        Limpia logs de auditoría antiguos según política de retención.
        
        Por defecto mantiene logs por 1 año.
        """
        if dias_retencion < 30:
            raise ValueError("No se pueden eliminar logs con menos de 30 días de antigüedad")
        
        eventos_eliminados = self._auditoria_repo.cleanup_old_events(dias_retencion)
        
        # Registrar la limpieza
        evento_limpieza = EventoAuditoria(
            id=None,
            usuario_id=None,  # Sistema
            accion=TipoAccion.LOGIN,  # Usar LOGIN como placeholder
            entidad="Sistema",
            entidad_id=None,
            descripcion=f"Limpieza automática: {eventos_eliminados} eventos eliminados (>{dias_retencion} días)"
        )
        self._auditoria_repo.save(evento_limpieza)
        
        return eventos_eliminados
