# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-24 12:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0003_auto_20161213_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurancetype',
            name='agen_code',
            field=models.ForeignKey(db_column='agen_code', default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='management.Agency', verbose_name='agency'),
        ),
    ]