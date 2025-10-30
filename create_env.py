"""
Script para crear el archivo .env con valores por defecto para desarrollo local.
Ejecutar: python create_env.py
"""
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Ruta del archivo .env
env_file = Path('.env')

# Verificar si ya existe
if env_file.exists():
    print("[INFO] El archivo .env ya existe. No se sobrescribira.")
    print(f"   Ubicacion: {env_file.absolute()}")
else:
    # Generar secret key
    secret_key = get_random_secret_key()
    
    # Contenido del archivo .env
    env_content = f"""# Django Configuration
DJANGO_SECRET_KEY={secret_key}
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Configuration (Base de datos secundaria - solo lectura)
# Ajustar estos valores según tu configuración de PostgreSQL
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_NAME=colegio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Email Configuration (Desarrollo local - console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@colegio.local
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@colegio.local
"""
    
    # Escribir el archivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("[OK] Archivo .env creado exitosamente!")
    print(f"   Ubicacion: {env_file.absolute()}")
    print("\n[IMPORTANTE] Ajusta las credenciales de PostgreSQL segun tu configuracion.")

