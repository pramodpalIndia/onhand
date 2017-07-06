# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-23 07:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0002_auto_20170221_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complianceserviceaction',
            name='cprs_id',
            field=models.ForeignKey(db_column='cprs_id', default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cprs_id_recorder', to='subscription.CompanyPersonRole', verbose_name='Recorded By'),
        ),
        migrations.AlterField(
            model_name='complianceserviceaction',
            name='csac_price',
            field=models.DecimalField(decimal_places=2, max_digits=18, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='complianceserviceaction',
            name='csac_service_date',
            field=models.DateField(verbose_name='servicedate'),
        ),
    ]
