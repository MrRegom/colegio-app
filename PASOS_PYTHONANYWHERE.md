# 🚀 PASOS RÁPIDOS PARA PYTHONANYWHERE

## Ejecuta estos comandos en orden:

```bash
# 1. Ir al proyecto y activar entorno
cd ~/colegio-app
source venv/bin/activate

# 2. Actualizar código
git pull origin main

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar sistema (VERÁS TODOS LOS ERRORES AQUÍ)
python verificar_y_actualizar.py

# 5. Ver el reporte completo
cat reporte_verificacion.txt

# 6. Limpiar datos (por si acaso)
python manage.py shell <<EOF
from django.db import connection
c = connection.cursor()
c.execute("UPDATE tba_bodega_articulos SET marca_id = NULL WHERE marca_id IS NOT NULL")
c.execute("UPDATE activo SET marca_id = NULL WHERE marca_id IS NOT NULL")
exit()
EOF

# 7. Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# 8. Recopilar estáticos
python manage.py collectstatic --noinput

# 9. REINICIAR: Ve a Dashboard → Web → Reload (botón verde)
```

## ✅ Verificación Final:

Después de reiniciar, verifica que funcione:
- `https://tuusuario.pythonanywhere.com/inventario/marcas/`
- `https://tuusuario.pythonanywhere.com/inventario/modelos/`

---

## 👥 Para tu Compañero (después de tu actualización):

```bash
# En su máquina local
git pull origin main
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

¡Listo para trabajar! 🎉

