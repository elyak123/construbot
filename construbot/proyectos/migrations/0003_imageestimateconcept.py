# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-06 19:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0002_auto_20180411_1424_unaccent_'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageEstimateConcept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='hola/bla/')),
                ('estimateconcept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.EstimateConcept')),
            ],
        ),
    ]
