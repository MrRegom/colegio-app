# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bodega', '0003_articulo_modelo_articulo_nombre_articulo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articulo',
            name='marca_old',
        ),
    ]

