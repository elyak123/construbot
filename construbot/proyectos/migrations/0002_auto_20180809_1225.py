# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-09 17:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='estimate',
            name='draft_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='draft_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='estimate',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Contrato'),
        ),
        migrations.AddField(
            model_name='estimate',
            name='supervised_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervised_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Cliente'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Cliente'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='sitio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Sitio'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='concept',
            name='estimate_concept',
            field=models.ManyToManyField(through='proyectos.EstimateConcept', to='proyectos.Estimate'),
        ),
        migrations.AddField(
            model_name='concept',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Contrato'),
        ),
        migrations.AddField(
            model_name='concept',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.Units'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Company'),
        ),
    ]