# 📋 Resumen Visual - Cómo Subir tu App y Verla en Línea

## 🎯 Flujo Completo (Imagina esto como una historia):

```
TU COMPUTADORA (Local)  →  GITHUB (Almacenamiento)  →  PYTHONANYWHERE (En Línea)
      ↓                           ↓                              ↓
   Trabajas aquí          Guardas tu código aquí        Tu app vive aquí
```

---

## 📝 PASO A PASO - Lo que harás HOY

### 🔵 PASO 1: Crear Repositorio en GitHub (5 minutos)
1. Ve a: https://github.com
2. Crea cuenta o inicia sesión
3. Crea nuevo repositorio llamado `colegio-app`
4. Copia la URL (ejemplo: `https://github.com/tu-usuario/colegio-app.git`)

### 🔵 PASO 2: Subir tu Código a GitHub (10 minutos)
Abre PowerShell o Git Bash en tu carpeta del proyecto y ejecuta:

```bash
cd C:\Users\mr.yo\Downloads\colegioapp\colegio

# Configurar Git (solo primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@gmail.com"

# Subir el proyecto
git init
git add .
git commit -m "Primera subida del proyecto"
git remote add origin https://github.com/TU-USUARIO/colegio-app.git
git branch -M main
git push -u origin main
```

**Cuando te pida contraseña**: Usa un **Personal Access Token** de GitHub (no tu contraseña normal). 
- Cómo crearlo: Ve a GitHub → Settings → Developer settings → Personal access tokens → Generate token

### 🔵 PASO 3: Configurar en PythonAnywhere (20-30 minutos)

#### 3.1. Crear cuenta:
1. Ve a: https://www.pythonanywhere.com
2. Registrarse (plan Beginner gratuito)

#### 3.2. Clonar el proyecto:
En la consola Bash de PythonAnywhere:
```bash
cd ~
git clone https://github.com/TU-USUARIO/colegio-app.git colegio
cd colegio
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.3. Configurar WSGI:
1. Ve a la pestaña **"Web"** en PythonAnywhere
2. Haz clic en **"WSGI configuration file"**
3. Copia el contenido de `wsgi_pythonanywhere_example.py`
4. **CAMBIAR**: Reemplaza todos los `yourusername` por tu usuario de PythonAnywhere
5. Genera SECRET_KEY:
   ```bash
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
6. Pega esa clave en el WSGI donde dice `GENERA_UNA_CLAVE_SECRETA...`
7. Guarda

#### 3.4. Configurar Static Files:
En la pestaña **"Web"**, sección Static files:
- URL: `/static/`
- Directory: `/home/tu-usuario/colegio/staticfiles`

- URL: `/media/`
- Directory: `/home/tu-usuario/colegio/media`

#### 3.5. Configurar base de datos:
```bash
cd ~/colegio
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 3.6. Recargar:
En la pestaña **"Web"**, haz clic en el botón verde **"Reload"**

### ✅ ¡LISTO! Tu app está en línea

Tu aplicación estará disponible en:
```
https://TU-USUARIO.pythonanywhere.com
```

**Ejemplo**: Si tu usuario es `juanperez`, será:
```
https://juanperez.pythonanywhere.com
```

---

## 👥 ¿Cómo ve tu compañero la app?

### ✅ OPCIÓN 1: Ver la App en Línea (Compartir URL)
Tu compañero puede simplemente:
1. Abrir su navegador web
2. Ir a: `https://TU-USUARIO.pythonanywhere.com`
3. **¡Ver la app funcionando!** 🌐

**Ventaja**: Puede ver los cambios en tiempo real sin hacer nada.

### ✅ OPCIÓN 2: Trabajar con el Código
Si tu compañero también quiere trabajar en el código:

**MAÑANA (cuando le toque a él):**

1. **En PythonAnywhere** (donde está desplegada la app):
   ```bash
   cd ~/colegio
   bash sync_pythonanywhere.sh
   ```
   O manualmente:
   ```bash
   source venv/bin/activate
   git pull origin main
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
   Luego recargar en la pestaña Web.

2. **En su computadora** (si quiere trabajar localmente):
   ```bash
   git clone https://github.com/TU-USUARIO/colegio-app.git
   cd colegio-app
   # Configurar entorno local...
   ```

---

## 🔄 Trabajo Colaborativo Diario

### Flujo Simple:

```
LUNES - TÚ:
  → Trabajas en tu código
  → git add . → git commit → git push
  → Tu compañero puede ver cambios en: https://TU-USUARIO.pythonanywhere.com

MARTES - TU COMPAÑERO:
  → En PythonAnywhere: git pull (obtiene tus cambios)
  → Trabaja en su código
  → git add . → git commit → git push
  → Tú puedes ver sus cambios en: https://TU-USUARIO.pythonanywhere.com

MIÉRCOLES - TÚ:
  → En PythonAnywhere: git pull (obtiene sus cambios)
  → Y así sucesivamente...
```

---

## 🎯 Resumen Ultra Rápido

### HOY (Tú):
1. ✅ Crear repositorio en GitHub
2. ✅ Subir código con Git
3. ✅ Configurar en PythonAnywhere
4. ✅ Tu app está en: `https://TU-USUARIO.pythonanywhere.com`

### MAÑANA (Tu Compañero):
- Puede ver la app en: `https://TU-USUARIO.pythonanywhere.com`
- Si trabaja: Hacer `git pull` en PythonAnywhere
- Al terminar: Hacer `git push` para subir sus cambios

---

## 🆘 Si algo no funciona

1. **No puedo subir a GitHub**: Revisa que tengas el Personal Access Token correcto
2. **Error en PythonAnywhere**: Revisa los logs en la pestaña "Web" → "Error log"
3. **La app no carga**: Asegúrate de hacer "Reload" después de cada cambio

---

## 📚 Archivos de Ayuda

- `GUIA_GIT_PARA_PRINCIPIANTES.md` → Guía completa de Git
- `COMANDOS_GIT_RAPIDOS.txt` → Comandos para copiar y pegar
- `QUICK_START_PYTHONANYWHERE.md` → Guía rápida de PythonAnywhere
- `PYTHONANYWHERE_DEPLOYMENT.md` → Guía detallada completa

---

**¡Comienza por el PASO 1 y sigue en orden! 🚀**

