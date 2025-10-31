# 📋 INSTRUCCIONES COMPLETAS - Módulo Inventario

## ✅ Estado Actual:
- ✓ Verificación completada: **SIN ERRORES**
- ✓ Todas las tablas creadas
- ✓ Migraciones aplicadas
- ✓ Código subido a Git

## 🚀 Para PythonAnywhere:

### Paso 1: Conectarse y actualizar código

En la **Bash Console** de PythonAnywhere:

```bash
# Ir al proyecto
cd ~/colegio-app  # (o el nombre de tu directorio)

# Activar entorno virtual
source venv/bin/activate

# Actualizar código
git pull origin main
```

### Paso 2: Instalar dependencias (si hay nuevas)

```bash
pip install -r requirements.txt
```

### Paso 3: Verificar sistema

```bash
python verificar_y_actualizar.py
cat reporte_verificacion.txt
```

### Paso 4: Limpiar datos (por si acaso)

```bash
python manage.py shell
```

En el shell:
```python
from django.db import connection
c = connection.cursor()
c.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
c.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
exit()
```

### Paso 5: Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 6: Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### Paso 7: Reiniciar aplicación

1. Ve al **Dashboard** → **Web**
2. Haz clic en el botón verde **"Reload"**

### Paso 8: Verificar que funciona

Visita tu sitio:
- `https://tuusuario.pythonanywhere.com/inventario/marcas/`
- `https://tuusuario.pythonanywhere.com/inventario/modelos/`

---

## 👥 Para tu Compañero:

### Cuando empiece a trabajar:

```bash
# 1. Actualizar código
git pull origin main

# 2. Activar entorno virtual
source venv/bin/activate  # o: workon colegio-app

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar sistema
python verificar_y_actualizar.py

# 5. Aplicar migraciones (si hay nuevas)
python manage.py makemigrations
python manage.py migrate

# 6. Iniciar servidor
python manage.py runserver
```

### Cuando termine de trabajar:

```bash
# 1. Ver qué cambió
git status

# 2. Agregar cambios
git add -A

# 3. Crear commit
git commit -m "Descripción de los cambios"

# 4. Subir cambios
git push origin main
```

---

## 🔍 Verificación Rápida:

Ejecuta el script de verificación para ver el estado completo:

```bash
python verificar_y_actualizar.py
cat reporte_verificacion.txt
```

Deberías ver:
- ✓ Todos los modelos se pueden importar
- ✓ Todas las tablas existen
- ✓ No hay datos conflictivos
- ✓ Todas las migraciones aplicadas
- ✓ No se encontraron errores

---

## 🎯 Nuevas Funcionalidades Disponibles:

1. **Gestor de Marcas**: `/inventario/marcas/`
2. **Gestor de Modelos**: `/inventario/modelos/`
3. **Gestor de Nombres de Artículos**: `/inventario/nombres-articulos/`
4. **Gestor de Sectores**: `/inventario/sectores/`
5. **Menú Gestores**: En el menú superior → Gestores → Catálogos de Productos

---

## ⚠️ Notas Importantes:

- **Solo una persona trabaja a la vez** - Coordina con tu compañero
- **Siempre `git pull` antes de empezar** - Para obtener últimos cambios
- **Siempre `git push` antes de terminar** - Para guardar cambios
- **Después de cambios, recarga la web** - Dashboard → Web → Reload

---

## 🆘 Si hay problemas:

1. Ejecuta: `python verificar_y_actualizar.py`
2. Revisa: `reporte_verificacion.txt`
3. Verifica logs: Dashboard → Web → Error log

