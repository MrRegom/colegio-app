#!/usr/bin/env python
"""
Script completo de verificación y actualización
Genera reporte detallado en archivo
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
except Exception as e:
    print(f"ERROR al inicializar Django: {e}")
    sys.exit(1)

from django.db import connection
from django.core.management import call_command
from io import StringIO

def log(msg, file=None):
    """Escribir mensaje tanto a consola como a archivo"""
    print(msg)
    if file:
        file.write(msg + "\n")
        file.flush()

def verificar_todo():
    """Ejecutar todas las verificaciones"""
    reporte = StringIO()
    errores = []
    
    log("="*70, reporte)
    log(f"REPORTE DE VERIFICACIÓN - {datetime.now()}", reporte)
    log("="*70, reporte)
    
    # 1. Verificar modelos
    log("\n[1/7] Verificando importación de modelos...", reporte)
    try:
        from apps.inventario.models import Marca, Modelo, NombreArticulo, SectorInventario
        from apps.bodega.models import Articulo
        from apps.activos.models import Activo
        log("✓ Todos los modelos se pueden importar", reporte)
    except Exception as e:
        log(f"✗ ERROR: {e}", reporte)
        errores.append(f"Modelos: {e}")
    
    # 2. Verificar tablas
    log("\n[2/7] Verificando tablas de base de datos...", reporte)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'inventario_%'
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        log(f"Tablas encontradas: {', '.join(tablas) if tablas else 'Ninguna'}", reporte)
        
        tablas_esperadas = ['inventario_marca', 'inventario_modelo', 
                           'inventario_nombre_articulo', 'inventario_sector']
        for tabla in tablas_esperadas:
            if tabla in tablas:
                log(f"✓ {tabla} existe", reporte)
            else:
                log(f"⚠ {tabla} NO existe (se creará)", reporte)
    except Exception as e:
        log(f"✗ ERROR: {e}", reporte)
        errores.append(f"Tablas: {e}")
    
    # 3. Verificar datos conflictivos
    log("\n[3/7] Verificando datos conflictivos...", reporte)
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM tba_bodega_articulos")
            total = cursor.fetchone()[0]
            log(f"Total de artículos: {total}", reporte)
            
            cursor.execute("SELECT COUNT(*) FROM tba_bodega_articulos WHERE marca_id IS NOT NULL")
            con_marca = cursor.fetchone()[0]
            log(f"Artículos con marca_id: {con_marca}", reporte)
            
            if con_marca > 0:
                # Intentar verificar si son válidos
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM tba_bodega_articulos a
                        WHERE a.marca_id IS NOT NULL 
                        AND a.marca_id NOT IN (SELECT id FROM inventario_marca)
                    """)
                    invalidos = cursor.fetchone()[0]
                    if invalidos > 0:
                        log(f"⚠ ADVERTENCIA: {invalidos} marca_id inválidos", reporte)
                        errores.append(f"Datos: {invalidos} marca_id inválidos")
                    else:
                        log("✓ Todos los marca_id son válidos", reporte)
                except Exception:
                    log("⚠ No se puede verificar (tabla inventario_marca no existe aún)", reporte)
        except Exception as e:
            log(f"⚠ No se pudo verificar artículos: {e}", reporte)
    except Exception as e:
        log(f"✗ ERROR: {e}", reporte)
        errores.append(f"Verificación datos: {e}")
    
    # 4. Verificar migraciones pendientes
    log("\n[4/7] Verificando migraciones...", reporte)
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            log(f"⚠ {len(plan)} migraciones pendientes:", reporte)
            for migration, backwards in plan[:5]:  # Mostrar solo las primeras 5
                log(f"   - {migration}", reporte)
        else:
            log("✓ Todas las migraciones aplicadas", reporte)
    except Exception as e:
        log(f"✗ ERROR: {e}", reporte)
        errores.append(f"Migraciones: {e}")
    
    # 5. Verificar referencias de modelos
    log("\n[5/7] Verificando referencias de modelos...", reporte)
    try:
        from apps.inventario.models import NombreArticulo
        campo = NombreArticulo._meta.get_field('categoria_recomendada')
        ref = campo.remote_field.model
        log(f"✓ Referencia correcta: {ref}", reporte)
    except Exception as e:
        log(f"✗ ERROR en referencia: {e}", reporte)
        errores.append(f"Referencias: {e}")
    
    # 6. Verificar configuración
    log("\n[6/7] Verificando configuración...", reporte)
    try:
        from django.conf import settings
        if 'apps.inventario' in settings.INSTALLED_APPS:
            log("✓ apps.inventario en INSTALLED_APPS", reporte)
        else:
            log("✗ apps.inventario NO está en INSTALLED_APPS", reporte)
            errores.append("Configuración: inventario no en INSTALLED_APPS")
    except Exception as e:
        log(f"✗ ERROR: {e}", reporte)
    
    # 7. Resumen final
    log("\n[7/7] Resumen final...", reporte)
    log("="*70, reporte)
    if errores:
        log(f"✗ Se encontraron {len(errores)} errores:", reporte)
        for i, error in enumerate(errores, 1):
            log(f"   {i}. {error}", reporte)
    else:
        log("✓ No se encontraron errores", reporte)
    log("="*70, reporte)
    
    # Guardar reporte
    with open('reporte_verificacion.txt', 'w', encoding='utf-8') as f:
        f.write(reporte.getvalue())
    
    print("\n" + "="*70)
    print("Reporte guardado en: reporte_verificacion.txt")
    print("="*70)
    print(reporte.getvalue())
    
    return len(errores) == 0

if __name__ == "__main__":
    try:
        exito = verificar_todo()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

