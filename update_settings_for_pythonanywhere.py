"""
Script para actualizar settings.py para que funcione tanto localmente como en PythonAnywhere.
Este script detecta automáticamente si está corriendo en PythonAnywhere y ajusta la configuración.

Ejecutar: python update_settings_for_pythonanywhere.py
"""
import os
import re
from pathlib import Path

# Detectar si estamos en PythonAnywhere
def is_pythonanywhere():
    """Detecta si el código está corriendo en PythonAnywhere"""
    return 'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or \
           'pythonanywhere' in str(Path.home())

# Ruta del archivo settings.py
settings_file = Path('core/settings.py')

if not settings_file.exists():
    print("Error: No se encuentra core/settings.py")
    exit(1)

# Leer el contenido actual
with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar si ya tiene la detección de PythonAnywhere
if 'is_pythonanywhere' in content:
    print("El archivo settings.py ya tiene la configuración para PythonAnywhere.")
    respuesta = input("¿Deseas actualizarlo de todas formas? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada.")
        exit(0)

# Crear el código para insertar después de las importaciones
pythonanywhere_config = '''
# Detección de PythonAnywhere
def is_pythonanywhere():
    """Detecta si el código está corriendo en PythonAnywhere"""
    return 'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or \\
           os.environ.get('PYTHONANYWHERE_DOMAIN', '').endswith('pythonanywhere.com')
'''

# Buscar dónde insertar (después de los imports y antes de BASE_DIR)
insertion_point = content.find('BASE_DIR = Path(__file__).resolve().parent.parent')

if insertion_point == -1:
    print("Error: No se encontró BASE_DIR en settings.py")
    exit(1)

# Buscar dónde termina la sección de imports
imports_end = content.rfind('\n\n', 0, insertion_point)
if imports_end == -1:
    imports_end = content.rfind('\n', 0, insertion_point)

# Insertar la función de detección
new_content = (
    content[:imports_end + 1] +
    pythonanywhere_config +
    '\n' +
    content[imports_end + 1:]
)

# Modificar la lectura del .env para que sea opcional en PythonAnywhere
env_reading_pattern = r"(environ\.Env\.read_env\(BASE_DIR / \"\.env\"\))"
replacement = r"""# Leer .env solo si existe (en PythonAnywhere las vars están en WSGI)
if Path(BASE_DIR / ".env").exists():
    \1"""

new_content = re.sub(env_reading_pattern, replacement, new_content)

# Modificar la configuración de variables de entorno para usar defaults
# SECRET_KEY con fallback
secret_key_pattern = r"SECRET_KEY = env\('DJANGO_SECRET_KEY'\)"
secret_key_replacement = r"""SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-production-12345')"""

new_content = re.sub(secret_key_pattern, secret_key_replacement, new_content)

# DEBUG con detección de PythonAnywhere
debug_pattern = r"DEBUG = env\.bool\('DJANGO_DEBUG'\)"
debug_replacement = r"""DEBUG = env.bool('DJANGO_DEBUG', default=not is_pythonanywhere())"""

new_content = re.sub(debug_pattern, debug_replacement, new_content)

# ALLOWED_HOSTS con default
allowed_hosts_pattern = r"ALLOWED_HOSTS = env\.list\('DJANGO_ALLOWED_HOSTS'\)"
allowed_hosts_replacement = r"""ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])"""

new_content = re.sub(allowed_hosts_pattern, allowed_hosts_replacement, new_content)

# Guardar el archivo
backup_file = Path('core/settings.py.backup')
if not backup_file.exists():
    print(f"Creando backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)

with open(settings_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] settings.py actualizado exitosamente para PythonAnywhere")
print(f"   Backup guardado en: {backup_file}")
print("\n[IMPORTANTE]:")
print("   1. Las variables de entorno en PythonAnywhere deben configurarse en el archivo WSGI")
print("   2. El archivo .env seguira funcionando localmente")
print("   3. Revisa el archivo y ajusta segun tus necesidades")

