# 🚀 Pasos Finales - Obtener URL para tu Compañero

## ✅ PASO 1: Tu código ya está en GitHub
Tu repositorio: https://github.com/MrRegom/colegio-app.git

---

## 📝 PASO 2: Configurar PythonAnywhere (30 minutos)

### 2.1. Crear cuenta en PythonAnywhere
1. Ve a: https://www.pythonanywhere.com
2. Haz clic en **"Sign up"** (Registrarse)
3. Elige el plan **"Beginner"** (gratuito)
4. Completa el registro

### 2.2. Clonar tu repositorio
1. En el dashboard de PythonAnywhere, ve a la pestaña **"Consoles"**
2. Haz clic en **"Bash"** para abrir una consola
3. Ejecuta estos comandos:

```bash
cd ~
git clone https://github.com/MrRegom/colegio-app.git colegio
cd colegio
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3. Configurar el archivo WSGI
1. Ve a la pestaña **"Web"** en PythonAnywhere
2. Haz clic en **"WSGI configuration file"** (al final de la página)
3. Reemplaza **TODO** el contenido con el código que está en `wsgi_pythonanywhere_example.py`
4. **IMPORTANTE**: Cambia estos valores:
   - Reemplaza todos los `yourusername` por tu usuario de PythonAnywhere
   - Ejemplo: Si tu usuario es `juanperez`, cambia `/home/yourusername/colegio` por `/home/juanperez/colegio`

5. Genera una SECRET_KEY segura:
   - En la consola Bash de PythonAnywhere:
   ```bash
   cd ~/colegio
   source venv/bin/activate
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   - Copia esa clave
   - En el archivo WSGI, reemplaza `GENERA_UNA_CLAVE_SECRETA_SEGURA_AQUI...` con esa clave

6. **Guarda el archivo WSGI**

### 2.4. Configurar Static Files
En la pestaña **"Web"**, sección **"Static files"**:
- URL: `/static/`
- Directory: `/home/TU-USUARIO/colegio/staticfiles`

- URL: `/media/`
- Directory: `/home/TU-USUARIO/colegio/media`

### 2.5. Ejecutar migraciones y crear superusuario
En la consola Bash:
```bash
cd ~/colegio
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 2.6. Recargar la aplicación
En la pestaña **"Web"**, haz clic en el botón verde **"Reload"** (abajo)

---

## 🌐 PASO 3: Tu URL está lista

Una vez configurado, tu aplicación estará disponible en:

```
https://TU-USUARIO.pythonanywhere.com
```

**Ejemplo**: Si tu usuario de PythonAnywhere es `juanperez`, la URL será:
```
https://juanperez.pythonanywhere.com
```

---

## 👥 Para tu Compañero

Tu compañero puede:
1. **Ver la app**: Solo abrir `https://TU-USUARIO.pythonanywhere.com` en su navegador
2. **Trabajar en el código**: Mañana, cuando le toque, ejecutar en PythonAnywhere:
   ```bash
   cd ~/colegio
   bash sync_pythonanywhere.sh
   ```
   O manualmente:
   ```bash
   source venv/bin/activate
   git pull origin main
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
   Luego recargar en la pestaña Web.

---

## ✅ Resumen

- ✅ Código subido a GitHub
- ⏳ Configurar PythonAnywhere (sigue los pasos arriba)
- ✅ Obtener URL: `https://TU-USUARIO.pythonanywhere.com`
- ✅ Compartir URL con tu compañero

---

## 🆘 Si algo sale mal

1. **Error al instalar paquetes**: Asegúrate de tener el entorno virtual activado (`source venv/bin/activate`)
2. **Error 500**: Revisa los logs en la pestaña "Web" → "Error log"
3. **Static files no cargan**: Verifica que ejecutaste `collectstatic` y que las rutas en la pestaña Web están correctas

---

**¡Sigue los pasos y en 30 minutos tu app estará en línea! 🚀**

