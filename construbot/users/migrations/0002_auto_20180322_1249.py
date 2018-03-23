# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-22 18:49
from __future__ import unicode_literals

import construbot.users.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=250, null=True)),
                ('company_name', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(blank=True, max_length=120, null=True, unique=True)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', construbot.users.models.ExtendUserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='last_supervised',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='user',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='user',
            name='user_creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Customer'),
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ManyToManyField(to='users.Company'),
        ),
        migrations.AddField(
            model_name='user',
            name='currently_at',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='currently_at', to='users.Company'),
        ),
        migrations.AddField(
            model_name='user',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.Customer'),
            preserve_default=False,
        ),
    ]