# Instrucciones para Subir Cambios a Git

## Pasos a seguir:

### 1. Abrir terminal en la carpeta del proyecto

```bash
cd c:\Users\mr.yo\Downloads\colegioapp\colegio
```

### 2. Verificar estado

```bash
git status
```

### 3. Agregar todos los archivos

```bash
git add .
```

### 4. Crear commit

```bash
git commit -m "feat: Agregar módulo completo de inventario con gestores de Marcas, Modelos, Nombres de Artículos y Sectores

- Crear modelos Marca, Modelo, NombreArticulo, SectorInventario
- Modificar Articulo y Activo para usar ForeignKey a catálogos
- Agregar código de barras auto-generable
- Crear CRUDs completos para todos los catálogos
- Implementar filtrado dinámico de modelos por marca
- Actualizar menú Gestores con nuevo submenú"
```

### 5. Subir a repositorio remoto

```bash
git push
```

## O usar el script automático:

Ejecuta el archivo `subir_git.bat` que creé, que hace todo automáticamente.

## Para tu compañero:

Después de que subas, tu compañero debe ejecutar:

```bash
git pull
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Archivos nuevos creados:

- `apps/inventario/models.py` - Modelos Marca, Modelo, NombreArticulo, SectorInventario
- `apps/inventario/forms.py` - Formularios para nuevos modelos
- `apps/inventario/views.py` - Vistas CRUD
- `apps/inventario/urls.py` - URLs
- `apps/inventario/admin.py` - Configuración admin
- `templates/inventario/*.html` - 12 templates nuevos
- `static/js/filtrar-modelos.js` - JavaScript para filtrado dinámico
- Migraciones en `apps/inventario/migrations/`

## Archivos modificados:

- `apps/bodega/models.py` - Agregado ForeignKey a catálogos
- `apps/activos/models.py` - Agregado ForeignKey a catálogos
- `apps/bodega/forms.py` - Actualizado ArticuloForm
- `apps/activos/forms.py` - Actualizado ActivoForm
- `templates/partials/topbar.html` - Nuevo menú "Catálogos de Productos"
- `templates/partials/base.html` - Script de filtrado dinámico

