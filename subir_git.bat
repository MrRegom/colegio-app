@echo off
echo ========================================
echo Subiendo cambios a Git
echo ========================================
echo.

echo 1. Verificando estado de Git...
git status
echo.

echo 2. Agregando todos los archivos...
git add .
echo.

echo 3. Creando commit...
git commit -m "feat: Agregar modulo completo de inventario con gestores de Marcas, Modelos, Nombres de Articulos y Sectores - Crear modelos Marca, Modelo, NombreArticulo, SectorInventario - Modificar Articulo y Activo para usar ForeignKey a catalogos - Agregar codigo de barras auto-generable - Crear CRUDs completos - Implementar filtrado dinamico de modelos por marca - Actualizar menu Gestores"
echo.

echo 4. Subiendo a repositorio remoto...
git push
echo.

echo ========================================
echo Proceso completado!
echo ========================================
pause

