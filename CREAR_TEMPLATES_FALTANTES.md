# Templates Faltantes - Instrucciones

## 📋 Templates que faltan crear:

Todos estos templates pueden crearse copiando el patrón de `templates/inventario/taller_list.html` y adaptando:
1. El título de la página
2. Los nombres de las variables (ej: `taller` → `bodega`, `departamento`, etc.)
3. Las URLs correspondientes
4. Los campos a mostrar en la tabla

## Lista de templates a crear:

### Bodegas (3 templates):
- `bodega_list.html` - Copiar de `taller_list.html`, cambiar URLs a `inventario:bodega_*`
- `bodega_form.html` - Copiar de `taller_form.html`, cambiar URLs
- `bodega_confirm_delete.html` - Copiar de `taller_confirm_delete.html`, cambiar URLs

### Estados Orden Compra (3 templates):
- `estado_orden_compra_list.html`
- `estado_orden_compra_form.html`
- `estado_orden_compra_confirm_delete.html`

### Estados Recepción (3 templates):
- `estado_recepcion_list.html`
- `estado_recepcion_form.html`
- `estado_recepcion_confirm_delete.html`

### Proveniencias (3 templates):
- `proveniencia_list.html`
- `proveniencia_form.html`
- `proveniencia_confirm_delete.html`

### Departamentos (3 templates):
- `departamento_list.html`
- `departamento_form.html`
- `departamento_confirm_delete.html`

### Equipos (5 templates):
- `equipo_list.html`
- `equipo_form.html`
- `equipo_detail.html`
- `equipo_confirm_delete.html`
- `mantenimiento_form.html`

**Total: 20 templates**

## ⚡ Solución rápida:

Por ahora, el sistema funcionará para los que ya tienen templates (Talleres, Tipos de Equipo). 
Para los demás, Django mostrará errores de template faltante hasta que se creen.

Puedo crear estos templates ahora si lo necesitas, o puedes crearlos manualmente copiando el patrón.

