# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 13:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField(blank=True)),
                ('voted_by', models.ManyToManyField(null=True, related_name='voted_time_options', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]