# Instrucciones para Actualizar PythonAnywhere

## 📋 Pasos para subir cambios a PythonAnywhere:

### 1. Conectarse a PythonAnywhere

Abre una **Bash Console** en PythonAnywhere (Dashboard → Consoles → New console → Bash).

### 2. Ir al directorio del proyecto

```bash
cd ~/colegio-app  # O el nombre de tu directorio en PythonAnywhere
# Si no sabes el nombre, ejecuta: ls -la para ver tus proyectos
```

### 3. Actualizar código desde Git

```bash
# Ver estado actual
git status

# Descartar cambios locales si hay conflictos (OPCIONAL - solo si es necesario)
# git reset --hard HEAD

# Actualizar desde repositorio
git pull origin main
# O si tu rama es diferente: git pull origin master
```

### 4. Activar el entorno virtual

```bash
# Activar el entorno virtual (ajusta la ruta si es diferente)
source ~/.virtualenvs/colegio-app/bin/activate
# O si usas mkvirtualenv:
# workon colegio-app
```

### 5. Instalar dependencias (si hay nuevas)

```bash
pip install -r requirements.txt
```

### 6. Limpiar datos antes de migrar (IMPORTANTE)

```bash
python manage.py shell
```

En el shell de Django, ejecuta:
```python
from django.db import connection
cursor = connection.cursor()

# Limpiar marca_id inválidos en Articulos
cursor.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")

# Limpiar marca_id inválidos en Activos  
cursor.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")

# Verificar que se limpiaron
cursor.execute("SELECT COUNT(*) FROM tba_bodega_articulos WHERE marca_id IS NOT NULL")
print(f"Artículos con marca_id: {cursor.fetchone()[0]}")

exit()
```

### 7. Crear y aplicar migraciones

```bash
# Crear migraciones (si faltan)
python manage.py makemigrations

# Aplicar todas las migraciones
python manage.py migrate

# Si hay errores, ejecuta:
# python manage.py migrate --run-syncdb
```

### 8. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 9. Reiniciar la aplicación web

1. Ve al Dashboard → **Web**
2. Haz clic en el botón verde **Reload** de tu aplicación web
3. O usa el comando:
   ```bash
   touch /var/www/tu_usuario_pythonanywhere_com_wsgi.py
   ```

### 10. Verificar que todo funciona

Visita tu sitio web y prueba:
- `/inventario/marcas/` - Debe funcionar
- `/inventario/modelos/` - Debe funcionar
- `/activos/crear/` - Debe cargar sin errores

## ⚠️ Si hay errores:

### Error: "no such table: inventario_marca"
```bash
# Aplicar migraciones específicas
python manage.py migrate inventario
python manage.py migrate bodega
python manage.py migrate activos
```

### Error: "Invalid model reference 'apps.bodega.Categoria'"
Este error significa que hay referencias incorrectas. Verifica que los archivos se actualizaron correctamente:
```bash
git status
git pull --force
```

### Error de migración de ForeignKey
Si falla la migración de `marca`:
```bash
# Revertir la migración problemática
python manage.py migrate bodega 0002

# Limpiar datos manualmente (ver paso 6)
# Luego aplicar migraciones nuevamente
python manage.py migrate
```

## 📝 Comandos Resumen (Copy-Paste):

```bash
# Todo en uno (ajusta las rutas según tu configuración)
cd ~/colegio-app
source ~/.virtualenvs/colegio-app/bin/activate
git pull origin main
pip install -r requirements.txt

# Limpiar datos
python manage.py shell <<EOF
from django.db import connection
c = connection.cursor()
c.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
c.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
exit()
EOF

# Migraciones
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Reiniciar (ve al Dashboard → Web → Reload)
```

## ✅ Verificación Final:

```bash
# Verificar que las tablas existen
python manage.py shell
```

En el shell:
```python
from django.db import connection
cursor = connection.cursor()

# Verificar tablas de inventario
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'inventario_%'")
print("Tablas de inventario:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

# Deberías ver:
# - inventario_marca
# - inventario_modelo  
# - inventario_nombre_articulo
# - inventario_sector

exit()
```

¡Listo! Tu aplicación debería estar actualizada en PythonAnywhere.

