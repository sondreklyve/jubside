# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-05 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20171023_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allergies',
            field=models.CharField(default='', max_length=100, verbose_name='Allergier'),
        ),
    ]
