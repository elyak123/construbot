# Generated by Django 2.1.9 on 2019-07-12 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0017_poblar_vertices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estimateconcept',
            name='alto',
        ),
        migrations.RemoveField(
            model_name='estimateconcept',
            name='ancho',
        ),
        migrations.RemoveField(
            model_name='estimateconcept',
            name='largo',
        ),
    ]
