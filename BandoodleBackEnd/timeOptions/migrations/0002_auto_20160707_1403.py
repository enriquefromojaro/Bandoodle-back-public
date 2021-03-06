# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 12:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        ('timeOptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeoption',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='timeoption',
            name='voted_by',
            field=models.ManyToManyField(related_name='voted_time_options', to=settings.AUTH_USER_MODEL),
        ),
    ]
