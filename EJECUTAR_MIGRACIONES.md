# Ejecutar Migraciones - Solución de Errores

## Error Actual:
- `no such table: inventario_marca`
- `no such column: activo.nombre_articulo_id`

## Solución:

### Paso 1: Detener el servidor (si está corriendo)
Presiona `Ctrl+C` en la terminal donde está corriendo `runserver`

### Paso 2: Ejecutar migraciones

Abre una nueva terminal en la carpeta del proyecto y ejecuta:

```bash
cd c:\Users\mr.yo\Downloads\colegioapp\colegio

# 1. Crear migraciones para bodega y activos (si faltan)
python manage.py makemigrations bodega
python manage.py makemigrations activos

# 2. Aplicar todas las migraciones
python manage.py migrate

# 3. Verificar que las tablas se crearon
python manage.py migrate inventario
python manage.py migrate bodega  
python manage.py migrate activos
```

### Paso 3: Verificar estado de migraciones

```bash
python manage.py showmigrations inventario
python manage.py showmigrations bodega
python manage.py showmigrations activos
```

### Paso 4: Reiniciar servidor

```bash
python manage.py runserver
```

## Si hay problemas:

Si aparecen errores de migraciones conflictivas, ejecuta:

```bash
python manage.py migrate --run-syncdb
```

O si necesitas forzar:

```bash
python manage.py migrate inventario --fake-initial
python manage.py migrate
```

## Verificar que las tablas existen:

```bash
python manage.py shell
```

En el shell de Django:

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'inventario_%'")
print('\n'.join([row[0] for row in cursor.fetchall()]))

# Deberías ver:
# inventario_marca
# inventario_modelo
# inventario_nombre_articulo
# inventario_sector
```

