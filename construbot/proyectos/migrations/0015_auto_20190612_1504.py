# Generated by Django 2.1.7 on 2019-06-12 15:04

import construbot.core.utils
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0014_auto_20190409_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=construbot.core.utils.get_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]