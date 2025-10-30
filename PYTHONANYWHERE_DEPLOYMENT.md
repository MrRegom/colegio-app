# Guía de Despliegue en PythonAnywhere

Esta guía explica cómo desplegar y trabajar colaborativamente en PythonAnywhere.

## 📋 Requisitos Previos

1. Cuenta en PythonAnywhere (gratuita o de pago)
2. Repositorio Git del proyecto (GitHub, GitLab, etc.)
3. Acceso a la cuenta por ambos desarrolladores

## 🚀 Configuración Inicial

### Paso 1: Configurar el Repositorio Git

**En tu máquina local (si aún no lo hiciste):**

```bash
# Asegúrate de tener Git inicializado
git init
git add .
git commit -m "Initial commit"
git remote add origin <URL_DE_TU_REPOSITORIO>
git push -u origin main  # o master según tu rama
```

### Paso 2: Clonar en PythonAnywhere

1. **Accede a la consola Bash en PythonAnywhere**
   - Ve a la pestaña "Consoles" en el dashboard
   - Crea una nueva consola Bash

2. **Navega a tu directorio home y clona el repositorio:**
```bash
cd ~
git clone <URL_DE_TU_REPOSITORIO> colegio
cd colegio
```

### Paso 3: Crear Entorno Virtual

```bash
# PythonAnywhere usa Python 3.x, verifica la versión
python3 --version

# Crea el entorno virtual
python3 -m venv venv

# Activa el entorno virtual
source venv/bin/activate

# Instala las dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

**En PythonAnywhere, NO uses archivo .env directamente. Configura las variables en el archivo WSGI.**

1. **Ve a la pestaña "Web" en el dashboard**
2. **Busca el archivo WSGI (debería ser algo como `yourusername_pythonanywhere_com_wsgi.py`)**
3. **Reemplaza todo el contenido del archivo WSGI con el siguiente código:**

```python
# Este archivo se encuentra en: /var/www/yourusername_pythonanywhere_com_wsgi.py
# O en el path que PythonAnywhere te indique

import os
import sys

# Path del proyecto (ajusta según tu estructura)
path = '/home/yourusername/colegio'  # ⚠️ CAMBIA 'yourusername' por tu usuario
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar variables de entorno ANTES de importar Django
os.environ['DJANGO_SECRET_KEY'] = 'TU_SECRET_KEY_AQUI_MINIMO_50_CARACTERES'
os.environ['DJANGO_DEBUG'] = 'False'  # False en producción
os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'

# PostgreSQL (si lo usas)
os.environ['POSTGRES_ENGINE'] = 'django.db.backends.postgresql'
os.environ['POSTGRES_NAME'] = 'tu_base_de_datos'
os.environ['POSTGRES_USER'] = 'tu_usuario_postgres'
os.environ['POSTGRES_PASSWORD'] = 'tu_password_postgres'
os.environ['POSTGRES_HOST'] = 'tu_host.postgres.pythonanywhere-services.com'
os.environ['POSTGRES_PORT'] = '5432'

# Email (configura según necesites)
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_USE_TLS'] = 'True'
os.environ['EMAIL_HOST_USER'] = 'tu_email@gmail.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'tu_password_de_aplicacion'
os.environ['DEFAULT_FROM_EMAIL'] = 'noreply@colegio.com'

# Ahora importar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

application = StaticFilesHandler(get_wsgi_application())
```

### Paso 5: Configurar el Settings para PythonAnywhere

Necesitamos modificar `core/settings.py` para que funcione tanto localmente como en PythonAnywhere. Usa el script `update_settings_for_pythonanywhere.py` que se proporciona.

### Paso 6: Ejecutar Migraciones

En la consola Bash de PythonAnywhere:

```bash
cd ~/colegio
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### Paso 7: Crear Superusuario (primera vez)

```bash
python manage.py createsuperuser
```

### Paso 8: Configurar el Servidor Web

1. **Ve a la pestaña "Web"**
2. **Configura los Static Files:**
   - URL: `/static/`
   - Directory: `/home/yourusername/colegio/staticfiles`
3. **Configura los Media Files:**
   - URL: `/media/`
   - pour directory: `/home/yourusername/colegio/media`
4. **Especifica el archivo WSGI:**
   - `/var/www/yourusername_pythonanywhere_com_wsgi.py` (o la ruta que PythonAnywhere te indique)

5. **Haz clic en el botón verde "Reload"**

## 🔄 Trabajo Colaborativo - Sincronización de Cambios

### Flujo de Trabajo Diario

**Cuando tú vas a trabajar (Desarrollador 1):**

```bash
# 1. Conectarte a PythonAnywhere
# 2. Abrir consola Bash

# 3. Ir al proyecto
cd ~/colegio

# 4. Desactivar el servidor web temporalmente (opcional)
# Ve a la pestaña Web y haz clic en "Reload" para aplicar cambios después

# 5. Actualizar desde Git
git pull origin main  # o master

# 6. Activar entorno virtual
source venv/bin/activate

# 7. Actualizar dependencias (si hay cambios)
pip install -r requirements.txt

# 8. Ejecutar migraciones (si hay cambios)
python manage.py migrate

# 9. Recopilar archivos estáticos (si hay cambios)
python manage.py collectstatic --noinput

# 10. Recargar la aplicación web
# Ve a la pestaña Web y haz clic en "Reload"
```

**Cuando tu compañero va a trabajar (Desarrollador 2):**

Repite los mismos pasos arriba.

### Script de Sincronización Automática

Se ha creado un script `sync_pythonanywhere.sh` que automatiza estos pasos. Úsalo así:

```bash
cd ~/colegio
bash sync_pythonanywhere.sh
```

## 🔧 Solución de Problemas Comunes

### Error: "ModuleNotFoundError"

```bash
# Asegúrate de tener el entorno virtual activado
source venv/bin/activate

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "Static files not found"

```bash
# Recopila los archivos estáticos
python manage.py collectstatic --noinput

# Verifica que la configuración en la pestaña Web esté correcta
```

### Error: "Database locked" (SQLite)

Si usas SQLite, PythonAnywhere puede tener problemas. Considera:
1. Usar PostgreSQL (gratis en PythonAnywhere)
2. O asegurarte de que solo una persona trabaja a la vez

### Error: "NoReverseMatch: 'apps' is not a registered namespace"

Este error aparece porque falta configurar correctamente las URLs. Verifica que:
1. Todas las apps están en `INSTALLED_APPS`
2. Las URLs están correctamente configuradas en `core/urls.py`

## 📝 Notas Importantes

1. **Siempre haz commit y push de tus cambios antes de terminar tu día de trabajo**
2. **Siempre haz `git pull` antes de empezar a trabajar**
3. **Comunica a tu compañero cuando terminas de trabajar**
4. **Evita trabajar simultáneamente - coordina los horarios**
5. **Las variables de entorno están en el archivo WSGI - no las compartas públicamente**

## 🔐 Seguridad

- **NUNCA** subas el archivo `.env` al repositorio
- **NUNCA** compartas las variables de entorno públicamente
- Usa contraseñas fuertes para la base de datos
- Usa `DEBUG = False` en producción

## 📚 Recursos Adicionales

- [Documentación de PythonAnywhere](https://help.pythonanywhere.com/)
- [Django en PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

