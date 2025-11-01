# Generated manually for Django 5.2.7

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Taller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('eliminado', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('ubicacion', models.CharField(blank=True, help_text='Ubicación física del taller en el colegio', max_length=200, null=True, verbose_name='Ubicación Física')),
                ('capacidad_maxima', models.IntegerField(blank=True, help_text='Capacidad máxima de personas que puede albergar', null=True, verbose_name='Capacidad Máxima')),
                ('equipamiento', models.TextField(blank=True, help_text='Descripción del equipamiento disponible en el taller', null=True, verbose_name='Equipamiento')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('responsable', models.ForeignKey(blank=True, help_text='Persona responsable del taller', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='talleres_responsable', to=settings.AUTH_USER_MODEL, verbose_name='Responsable')),
            ],
            options={
                'verbose_name': 'Taller',
                'verbose_name_plural': 'Talleres',
                'db_table': 'inventario_taller',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='TipoEquipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('eliminado', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('requiere_mantenimiento', models.BooleanField(default=True, help_text='Indica si este tipo de equipo requiere mantenimiento regular', verbose_name='Requiere Mantenimiento')),
                ('periodo_mantenimiento_dias', models.IntegerField(blank=True, help_text='Período recomendado entre mantenimientos en días', null=True, verbose_name='Período de Mantenimiento (días)')),
            ],
            options={
                'verbose_name': 'Tipo de Equipo',
                'verbose_name_plural': 'Tipos de Equipos',
                'db_table': 'inventario_tipo_equipo',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('eliminado', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('codigo', models.CharField(max_length=50, unique=True, verbose_name='Código/Patrimonio')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('marca', models.CharField(blank=True, max_length=100, null=True, verbose_name='Marca')),
                ('modelo', models.CharField(blank=True, max_length=100, null=True, verbose_name='Modelo')),
                ('numero_serie', models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='Número de Serie')),
                ('fecha_adquisicion', models.DateField(blank=True, null=True, verbose_name='Fecha de Adquisición')),
                ('valor_adquisicion', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Valor de Adquisición')),
                ('estado', models.CharField(choices=[('DISPONIBLE', 'Disponible'), ('EN_USO', 'En Uso'), ('MANTENIMIENTO', 'En Mantenimiento'), ('DADO_DE_BAJA', 'Dado de Baja'), ('PRESTADO', 'Prestado')], default='DISPONIBLE', max_length=20, verbose_name='Estado')),
                ('ubicacion_actual', models.CharField(blank=True, help_text='Ubicación física actual del equipo', max_length=200, null=True, verbose_name='Ubicación Actual')),
                ('fecha_ultimo_mantenimiento', models.DateField(blank=True, null=True, verbose_name='Fecha Último Mantenimiento')),
                ('fecha_proximo_mantenimiento', models.DateField(blank=True, null=True, verbose_name='Fecha Próximo Mantenimiento')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipos_responsable', to=settings.AUTH_USER_MODEL, verbose_name='Responsable')),
                ('taller', models.ForeignKey(blank=True, help_text='Taller al que pertenece o está asignado el equipo', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipos', to='inventario.taller', verbose_name='Taller')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipos', to='inventario.tipoequipo', verbose_name='Tipo de Equipo')),
            ],
            options={
                'verbose_name': 'Equipo',
                'verbose_name_plural': 'Equipos',
                'db_table': 'inventario_equipo',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='MantenimientoEquipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('eliminado', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('fecha_mantenimiento', models.DateField(verbose_name='Fecha de Mantenimiento')),
                ('tipo_mantenimiento', models.CharField(choices=[('PREVENTIVO', 'Preventivo'), ('CORRECTIVO', 'Correctivo'), ('CALIBRACION', 'Calibración'), ('REVISION', 'Revisión')], max_length=20, verbose_name='Tipo de Mantenimiento')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('realizado_por', models.CharField(blank=True, help_text='Nombre del técnico o empresa que realizó el mantenimiento', max_length=200, null=True, verbose_name='Realizado Por')),
                ('costo', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Costo')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('proximo_mantenimiento', models.DateField(blank=True, null=True, verbose_name='Próximo Mantenimiento Programado')),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mantenimientos', to='inventario.equipo', verbose_name='Equipo')),
            ],
            options={
                'verbose_name': 'Mantenimiento de Equipo',
                'verbose_name_plural': 'Mantenimientos de Equipos',
                'db_table': 'inventario_mantenimiento_equipo',
                'ordering': ['-fecha_mantenimiento'],
            },
        ),
    ]

