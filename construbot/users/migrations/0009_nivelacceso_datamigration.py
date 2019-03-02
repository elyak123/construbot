# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-19 15:10
from __future__ import unicode_literals
from django.db import migrations
from django.contrib.auth import get_user_model
from django.db.models import Q


def crear_niveles_acceso(nivel):
    Nivel = nivel
    args = [
        {'nombre': 'Auxiliar', 'nivel': 1},
        {'nombre': 'Coordinador', 'nivel': 2},
        {'nombre': 'Director', 'nivel': 3},
        {'nombre': 'Corporativo', 'nivel': 4},
        {'nombre': 'Soporte', 'nivel': 5}
    ]
    return [Nivel.objects.create(**kwargs) for kwargs in args]


def nivelaccesso_datamigration(apps, schema_editor):
    _User = get_user_model()
    User = apps.get_model(_User._meta.app_label, _User._meta.model_name)
    Nivel = apps.get_model('users', 'NivelAcceso')
    Group = apps.get_model('auth', 'Group')
    admin_group, admin_created = Group.objects.get_or_create(name='Administrators')
    proyecto_group, proy_created = Group.objects.get_or_create(name='Proyectos')
    users_group, users_created = Group.objects.get_or_create(name='Users')
    niveles = crear_niveles_acceso(Nivel)
    acceso_auxiliar = niveles[0]
    # acceso_coordinador = niveles[1] # por el momento no se usa
    acceso_director = niveles[2]
    acceso_corporativo = niveles[3]
    auxiliares = User.objects.filter(groups=proyecto_group)
    auxiliares.update(nivel_acceso=acceso_auxiliar)
    directores = User.objects.filter(Q(groups=admin_group) | Q(groups=users_group))
    directores.update(nivel_acceso=acceso_director)
    corporativos = User.objects.filter(Q(groups=admin_group) & Q(groups=users_group))
    corporativos.update(nivel_acceso=acceso_corporativo)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_creacion_nivelacceso'),
    ]

    operations = [
        migrations.RunPython(nivelaccesso_datamigration)
    ]