# Solución Rápida - Error de Migración

## ✅ El Push a Git fue EXITOSO
Los cambios están en el repositorio.

## ⚠️ Error al aplicar migración:

```
IntegrityError: tba_bodega_articulos.marca_id contains a value 'Marca' 
that does not have a corresponding value in inventario_marca.id
```

## 🔧 Solución (Ejecutar en tu terminal):

```bash
# Opción 1: Limpiar datos y aplicar migración
python manage.py shell
```

En el shell de Django:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
cursor.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
exit()
```

Luego:
```bash
python manage.py migrate
```

## 📝 O usar el script:

Ejecuta `FIX_MIGRACION.bat` que creé.

## Para tu compañero:

Después de hacer `git pull`, debe ejecutar:

```bash
# Limpiar datos primero
python manage.py shell
# (ejecutar los comandos SQL de arriba)

# Aplicar migraciones
python manage.py migrate

# Reiniciar servidor
python manage.py runserver
```

