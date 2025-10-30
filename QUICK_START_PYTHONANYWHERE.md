# Inicio Rápido - PythonAnywhere

## Pasos Rápidos para Desplegar

### 1. Preparar el Repositorio (primera vez)

```bash
# En tu máquina local
git init
git add .
git commit -m "Initial commit"
git remote add origin <URL_DE_TU_REPOSITORIO>
git push -u origin main
```

### 2. En PythonAnywhere - Primera Configuración

```bash
# En la consola Bash de PythonAnywhere
cd ~
git clone <URL_DE_TU_REPOSITORIO> colegio
cd colegio
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar el Archivo WSGI

1. Ve a la pestaña **"Web"** en PythonAnywhere
2. Haz clic en **"WSGI configuration file"**
3. Reemplaza TODO el contenido con el código de `wsgi_pythonanywhere_example.py`
4. **IMPORTANTE**: Cambia todos los `yourusername` por tu usuario real de PythonAnywhere
5. Genera una SECRET_KEY segura:
   ```bash
   cd ~/colegio
   source venv/bin/activate
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
6. Copia esa clave y reemplázala en el WSGI donde dice `GENERA_UNA_CLAVE_SECRETA...`
7. Guarda el archivo

### 4. Configurar Static y Media Files

En la pestaña **"Web"**, sección **"Static files"**:

- URL: `/static/`
- Directory: `/home/yourusername/colegio/staticfiles`

- URL: `/media/`
- Directory: `/home/yourusername/colegio/media`

### 5. Ejecutar Migraciones y Crear Superusuario

```bash
cd ~/colegio
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6. Recargar la Aplicación

En la pestaña **"Web"**, haz clic en el botón verde **"Reload"**.

## 🔄 Sincronizar Cambios (Cada Día de Trabajo)

### Cuando Empiezas a Trabajar:

```bash
cd ~/colegio
bash sync_pythonanywhere.sh
```

O manualmente:

```bash
cd ~/colegio
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Luego ve a la pestaña **"Web"** y haz clic en **"Reload"**.

### Cuando Terminas de Trabajar:

```bash
# En tu máquina local
git add .
git commit -m "Descripcion de los cambios"
git push origin main
```

**IMPORTANTE**: Siempre haz push antes de terminar para que tu compañero tenga los cambios al día siguiente.

## ⚠️ Recordatorios Importantes

1. **Solo una persona trabaja a la vez** - Coordina con tu compañero
2. **Siempre `git pull` antes de empezar** - Para obtener los últimos cambios
3. **Siempre `git push` antes de terminar** - Para guardar tus cambios
4. **Después de cambios, recarga la web** - Ve a "Web" > "Reload"
5. **Las variables de entorno están en el WSGI** - No uses archivo .env en producción

## 🆘 Si Algo Sale Mal

1. Verifica que el entorno virtual esté activado: `source venv/bin/activate`
2. Verifica las dependencias: `pip install -r requirements.txt`
3. Verifica las migraciones: `python manage.py migrate`
4. Verifica los archivos estáticos: `python manage.py collectstatic --noinput`
5. Revisa los logs de error en la pestaña **"Web"** > **"Error log"**

## 📚 Documentación Completa

Lee `PYTHONANYWHERE_DEPLOYMENT.md` para más detalles.

