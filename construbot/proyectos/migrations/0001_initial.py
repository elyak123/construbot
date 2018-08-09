# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-09 17:25
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente_name', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('concept_text', models.TextField()),
                ('total_cuantity', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='cuantity')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='unit_price')),
            ],
            options={
                'verbose_name': 'Concepto',
                'verbose_name_plural': 'Conceptos',
            },
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.IntegerField()),
                ('code', models.CharField(blank=True, max_length=35, null=True)),
                ('fecha', models.DateField()),
                ('contrato_name', models.CharField(max_length=300)),
                ('contrato_shortName', models.CharField(max_length=80)),
                ('status', models.BooleanField(default=True)),
                ('file', models.FileField(blank=True, null=True, upload_to=core.utils.get_directory_path)),
                ('monto', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='monto')),
            ],
            options={
                'verbose_name': 'Contrato',
                'verbose_name_plural': 'Contratos',
            },
        ),
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destinatario_text', models.CharField(max_length=80)),
                ('puesto', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Destinatario',
                'verbose_name_plural': 'Destinatarios',
            },
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consecutive', models.IntegerField()),
                ('start_date', models.DateField(verbose_name='start_date')),
                ('finish_date', models.DateField(verbose_name='finish_date')),
                ('draft_date', models.DateField(auto_now=True, verbose_name='draft_date')),
                ('auth_date', models.DateField(blank=True, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('invoiced', models.BooleanField(default=False)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('auth_by', models.ManyToManyField(blank=True, to='proyectos.Destinatario')),
                ('auth_by_gen', models.ManyToManyField(blank=True, related_name='generator', to='proyectos.Destinatario')),
            ],
            options={
                'verbose_name': 'Estimacion',
                'verbose_name_plural': 'Estimaciones',
            },
        ),
        migrations.CreateModel(
            name='EstimateConcept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuantity_estimated', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='cuantity_estimated')),
                ('observations', models.TextField(blank=True, null=True)),
                ('largo', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='largo')),
                ('ancho', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='ancho')),
                ('alto', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='alto')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Concept')),
                ('estimate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Estimate')),
            ],
            options={
                'verbose_name': 'Estimado por Concepto',
                'verbose_name_plural': 'Estimaciones por Conceptos',
            },
        ),
        migrations.CreateModel(
            name='ImageEstimateConcept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='hola/bla/')),
                ('estimateconcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.EstimateConcept')),
            ],
        ),
        migrations.CreateModel(
            name='Sitio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sitio_name', models.CharField(max_length=80)),
                ('sitio_location', models.CharField(blank=True, max_length=80, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Cliente')),
            ],
            options={
                'verbose_name': 'Sitio',
                'verbose_name_plural': 'Sitios',
            },
        ),
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Unidad',
                'verbose_name_plural': 'Unidades',
            },
        ),
    ]
