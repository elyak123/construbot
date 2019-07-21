# Generated by Django 2.1.9 on 2019-07-07 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0015_auto_20190612_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vertices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, verbose_name='Nombre del Vertice')),
                ('largo', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='largo')),
                ('ancho', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='ancho')),
                ('alto', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='alto')),
                ('piezas', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='número de piezas')),
            ],
        ),
        migrations.AddField(
            model_name='vertices',
            name='estimateconcept',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyectos.EstimateConcept'),
        ),
    ]
