# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-09-30 13:03
from __future__ import unicode_literals

import construbot.core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0003_auto_20180809_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=construbot.core.utils.get_directory_path),
        ),
    ]
