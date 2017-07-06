# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-23 00:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cprs_id',
            field=models.ForeignKey(db_column='cprs_id', on_delete=django.db.models.deletion.DO_NOTHING, to='subscription.CompanyPersonRole', verbose_name='companypersonrole'),
        ),
    ]