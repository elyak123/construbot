# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-19 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_new'),
    ]
    operations = [
        migrations.CreateModel(
            name='NivelAcceso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.IntegerField(unique=True)),
                ('nombre', models.CharField(max_length=80, verbose_name='Nivel de Acceso')),
            ],
            options={
                'verbose_name': 'NivelAcceso',
                'verbose_name_plural': 'NivelAccesos',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='nivel_acceso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.NivelAcceso'),
        ),
    ]
