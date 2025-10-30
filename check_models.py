#!/usr/bin/env python
"""Script para verificar que los modelos se pueden importar correctamente."""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, r'C:\Users\manue\Proyectos\proyectotic')

try:
    django.setup()
    print("Django configurado correctamente")

    # Importar modelos
    from apps.accounts.models import (
        AuthEstado,
        AuthUserEstado,
        AuthLogAccion,
        AuthLogs,
        HistorialLogin
    )
    print("\nModelos importados correctamente:")
    print("  - AuthEstado")
    print("  - AuthUserEstado")
    print("  - AuthLogAccion")
    print("  - AuthLogs")
    print("  - HistorialLogin")

    # Verificar campos de cada modelo
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE CAMPOS EN MODELOS")
    print("=" * 80)

    print("\n1. AuthEstado:")
    for field in AuthEstado._meta.get_fields():
        print(f"   - {field.name} ({field.__class__.__name__})")

    print("\n2. AuthUserEstado:")
    for field in AuthUserEstado._meta.get_fields():
        print(f"   - {field.name} ({field.__class__.__name__})")

    print("\n3. AuthLogAccion:")
    for field in AuthLogAccion._meta.get_fields():
        print(f"   - {field.name} ({field.__class__.__name__})")

    print("\n4. AuthLogs:")
    for field in AuthLogs._meta.get_fields():
        print(f"   - {field.name} ({field.__class__.__name__})")

    print("\n5. HistorialLogin:")
    for field in HistorialLogin._meta.get_fields():
        print(f"   - {field.name} ({field.__class__.__name__})")

    print("\n" + "=" * 80)
    print("VERIFICACIÓN COMPLETADA - No se encontraron errores")
    print("=" * 80)

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
