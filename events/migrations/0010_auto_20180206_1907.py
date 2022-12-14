# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-06 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_event_hidden_to_public'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='hidden_to_public',
        ),
        migrations.AddField(
            model_name='event',
            name='hidden_to_guests',
            field=models.BooleanField(default=False, help_text='Hvis arrangementet av en eller annen grunn ikke skal være synlig for offentligheten, men bare for innloggede brukere.', verbose_name='Skjult for gjester'),
        ),
    ]
