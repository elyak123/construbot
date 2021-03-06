# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-29 20:21

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def poblar_unidades(apps, schema_editor):
    Concept = apps.get_model('proyectos', 'Concept')
    Units = apps.get_model('proyectos', 'Units')
    Company = apps.get_model('users', 'Company')
    for concepto in Concept.objects.all():
        company = concepto.project.cliente.company
        try:
            Units.objects.get(unit=concepto.unit.unit, company=company)
        except Units.DoesNotExist:
            unidad = Units.objects.get(unit=concepto.unit.unit)
            unidad.company = company
        except Units.DoesNotExist as e:
            raise e
    left_over = Units.objects.filter(company__isnull=True)
    company = Company.objects.first()
    left_over.update(company=company)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_new'),
        ('proyectos', '0009_auto_20181213_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='units',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Company'),
        ),
        migrations.AlterField(
            model_name='units',
            name='unit',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(poblar_unidades),
        migrations.AlterField(
            model_name='units',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Company'),
            preserve_default=False
        ),
        migrations.AlterUniqueTogether(
            name='units',
            unique_together=set([('unit', 'company')]),
        ),
    ]
