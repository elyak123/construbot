# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-27 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20181029_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]
