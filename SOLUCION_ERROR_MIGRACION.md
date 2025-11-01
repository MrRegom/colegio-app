# Solución Error de Migración - Foreign Key

## Error:
```
IntegrityError: The row in table 'tba_bodega_articulos' with primary key '1' has an invalid foreign key: 
tba_bodega_articulos.marca_id contains a value 'Marca' that does not have a corresponding value in inventario_marca.id.
```

## Problema:
Hay registros existentes en la tabla `tba_bodega_articulos` que tienen valores de texto (como 'Marca') en el campo `marca`, pero ahora `marca` es un ForeignKey que debe apuntar a `inventario_marca.id`.

## Solución Rápida (Recomendada):

### Opción 1: Limpiar datos manualmente antes de migrar

```bash
# 1. Abrir shell de Django
python manage.py shell

# 2. Limpiar los valores de marca que son texto
from django.db import connection
cursor = connection.cursor()

# Ver qué hay en marca_id
cursor.execute("SELECT id, marca_id FROM tba_bodega_articulos WHERE marca_id IS NOT NULL LIMIT 10")
print(cursor.fetchall())

# Limpiar todos los marca_id que no sean números válidos
cursor.execute("""
    UPDATE tba_bodega_articulos 
    SET marca_id = NULL 
    WHERE marca_id IS NOT NULL 
    AND typeof(marca_id) != 'integer'
""")

# O simplemente limpiar todos si no hay datos importantes
cursor.execute("UPDATE tba_bodega_articulos SET marca_id = NULL")
```

### Opción 2: Eliminar la migración problemática y recrearla

```bash
# 1. Revertir la migración problemática
python manage.py migrate bodega 0002

# 2. Eliminar el archivo de migración
# Borrar: apps/bodega/migrations/0003_articulo_modelo_articulo_nombre_articulo_and_more.py

# 3. Recrear la migración
python manage.py makemigrations bodega

# 4. Aplicar
python manage.py migrate
```

### Opción 3: Editar la migración para que limpie datos primero

He creado una migración `0004_limpiar_marcas_antes_fk.py` que limpia los datos antes de convertir.

```bash
# Aplicar migración de limpieza primero
python manage.py migrate bodega 0004

# Luego aplicar la 0003
python manage.py migrate bodega 0003
```

## Solución Recomendada (Más Segura):

1. **Hacer backup de la BD primero**
2. **Limpiar datos manualmente en el shell de Django**
3. **Aplicar migraciones**

```bash
python manage.py shell
```

En el shell:
```python
from django.db import connection
cursor = connection.cursor()

# Ver estado actual
cursor.execute("SELECT id, sku, nombre, marca FROM tba_bodega_articulos LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Limpiar marca_id (si existe como FK ya)
cursor.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")

# Salir
exit()
```

Luego:
```bash
python manage.py migrate
```

