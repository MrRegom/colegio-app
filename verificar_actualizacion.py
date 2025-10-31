#!/usr/bin/env python
"""
Script de verificación completa para actualización de inventario
Ejecuta verificaciones paso a paso y muestra errores detallados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.core.management.base import CommandError

def print_step(num, desc):
    print(f"\n{'='*60}")
    print(f"PASO {num}: {desc}")
    print(f"{'='*60}")

def check_models():
    """Verificar que los modelos se pueden importar"""
    print_step(1, "Verificando importación de modelos")
    try:
        from apps.inventario.models import Marca, Modelo, NombreArticulo, SectorInventario
        from apps.bodega.models import Articulo
        from apps.activos.models import Activo
        print("✓ Todos los modelos se pueden importar correctamente")
        return True
    except Exception as e:
        print(f"✗ ERROR al importar modelos: {e}")
        return False

def check_database_tables():
    """Verificar que las tablas existen o están listas para crearse"""
    print_step(2, "Verificando tablas de base de datos")
    try:
        cursor = connection.cursor()
        
        # Verificar tablas de inventario
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'inventario_%'
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        
        tablas_esperadas = [
            'inventario_marca',
            'inventario_modelo',
            'inventario_nombre_articulo',
            'inventario_sector'
        ]
        
        print(f"Tablas de inventario encontradas: {tablas}")
        
        for tabla in tablas_esperadas:
            if tabla in tablas:
                print(f"✓ {tabla} existe")
            else:
                print(f"⚠ {tabla} NO existe (se creará con migraciones)")
        
        return True
    except Exception as e:
        print(f"✗ ERROR al verificar tablas: {e}")
        return False

def check_data_conflicts():
    """Verificar conflictos de datos"""
    print_step(3, "Verificando conflictos de datos")
    try:
        cursor = connection.cursor()
        
        # Verificar Articulos
        try:
            cursor.execute("SELECT COUNT(*) FROM tba_bodega_articulos WHERE marca_id IS NOT NULL")
            count = cursor.fetchone()[0]
            print(f"Artículos con marca_id: {count}")
            
            if count > 0:
                # Verificar si los valores son válidos
                cursor.execute("""
                    SELECT marca_id FROM tba_bodega_articulos 
                    WHERE marca_id IS NOT NULL 
                    LIMIT 5
                """)
                valores = cursor.fetchall()
                print(f"Valores de marca_id encontrados: {valores}")
                
                # Intentar verificar si son IDs válidos
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM tba_bodega_articulos a
                        WHERE a.marca_id IS NOT NULL 
                        AND a.marca_id NOT IN (SELECT id FROM inventario_marca)
                    """)
                    invalidos = cursor.fetchone()[0]
                    if invalidos > 0:
                        print(f"⚠ ADVERTENCIA: {invalidos} artículos tienen marca_id inválidos")
                        print("   Necesitan limpieza antes de migrar")
                        return False
                except Exception:
                    print("⚠ No se pudo verificar validez (tabla inventario_marca puede no existir aún)")
        except Exception as e:
            print(f"⚠ No se pudo verificar artículos: {e}")
        
        print("✓ Verificación de datos completada")
        return True
    except Exception as e:
        print(f"✗ ERROR al verificar datos: {e}")
        return False

def check_migrations():
    """Verificar estado de migraciones"""
    print_step(4, "Verificando estado de migraciones")
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠ Hay {len(plan)} migraciones pendientes:")
            for migration, backwards in plan:
                print(f"   - {migration}")
        else:
            print("✓ Todas las migraciones están aplicadas")
        
        return True
    except Exception as e:
        print(f"✗ ERROR al verificar migraciones: {e}")
        return False

def clean_data():
    """Limpiar datos conflictivos"""
    print_step(5, "Limpiando datos conflictivos")
    try:
        cursor = connection.cursor()
        
        # Limpiar Articulos
        cursor.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
        articulos_limpiados = cursor.rowcount
        print(f"✓ Limpiados {articulos_limpiados} artículos")
        
        # Limpiar Activos
        try:
            cursor.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
            activos_limpiados = cursor.rowcount
            print(f"✓ Limpiados {activos_limpiados} activos")
        except Exception:
            print("⚠ No se pudo limpiar activos (tabla puede no tener marca_id aún)")
        
        return True
    except Exception as e:
        print(f"✗ ERROR al limpiar datos: {e}")
        return False

def apply_migrations():
    """Aplicar migraciones"""
    print_step(6, "Aplicando migraciones")
    try:
        call_command('migrate', verbosity=2, interactive=False)
        print("✓ Migraciones aplicadas correctamente")
        return True
    except Exception as e:
        print(f"✗ ERROR al aplicar migraciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_final_state():
    """Verificar estado final"""
    print_step(7, "Verificación final")
    try:
        # Verificar que las tablas existen
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'inventario_%'
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        
        tablas_esperadas = [
            'inventario_marca',
            'inventario_modelo',
            'inventario_nombre_articulo',
            'inventario_sector'
        ]
        
        todas_existen = all(tabla in tablas for tabla in tablas_esperadas)
        
        if todas_existen:
            print("✓ Todas las tablas de inventario existen")
            
            # Contar registros
            for tabla in tablas_esperadas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   - {tabla}: {count} registros")
            
            return True
        else:
            print("⚠ Algunas tablas no existen aún")
            return False
    except Exception as e:
        print(f"✗ ERROR en verificación final: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("SCRIPT DE VERIFICACIÓN - MÓDULO DE INVENTARIO")
    print("="*60)
    
    resultados = []
    
    # Paso 1: Verificar modelos
    resultados.append(("Modelos", check_models()))
    
    # Paso 2: Verificar tablas
    resultados.append(("Tablas", check_database_tables()))
    
    # Paso 3: Verificar datos
    resultados.append(("Datos", check_data_conflicts()))
    
    # Paso 4: Verificar migraciones
    resultados.append(("Migraciones", check_migrations()))
    
    # Preguntar si limpiar datos
    print("\n" + "="*60)
    respuesta = input("¿Deseas limpiar datos conflictivos ahora? (s/n): ")
    if respuesta.lower() == 's':
        resultados.append(("Limpieza", clean_data()))
        
        # Aplicar migraciones
        respuesta2 = input("¿Aplicar migraciones ahora? (s/n): ")
        if respuesta2.lower() == 's':
            resultados.append(("Aplicar Migraciones", apply_migrations()))
            resultados.append(("Verificación Final", verify_final_state()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    for nombre, resultado in resultados:
        estado = "✓ OK" if resultado else "✗ ERROR"
        print(f"{nombre}: {estado}")
    
    exitos = sum(1 for _, r in resultados if r)
    total = len(resultados)
    print(f"\nTotal: {exitos}/{total} verificaciones exitosas")
    
    if exitos == total:
        print("\n🎉 ¡Todo está correcto! Puedes proceder con la actualización.")
    else:
        print("\n⚠ Hay errores que deben corregirse antes de continuar.")

if __name__ == "__main__":
    main()

