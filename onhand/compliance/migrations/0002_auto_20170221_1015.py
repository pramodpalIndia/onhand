# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-21 10:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FactorValue',
            fields=[
                ('fval_id', models.AutoField(primary_key=True, serialize=False)),
                ('fval_value', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='value')),
                ('csrv', models.ForeignKey(db_column='csrv_id', on_delete=django.db.models.deletion.DO_NOTHING, to='compliance.ComplianceService', verbose_name='Compliance')),
            ],
            options={
                'verbose_name_plural': 'factorsvalues',
                'db_table': 'oh_factor_value',
                'verbose_name': 'factorvalue',
            },
        ),
        migrations.AlterField(
            model_name='factor',
            name='fact_code',
            field=models.CharField(db_column='fact_code', max_length=6, primary_key=True, serialize=False, verbose_name='code'),
        ),
        migrations.AddField(
            model_name='factorvalue',
            name='fact',
            field=models.ForeignKey(db_column='fact_code', on_delete=django.db.models.deletion.DO_NOTHING, to='compliance.Factor', verbose_name='code'),
        ),
        migrations.AlterUniqueTogether(
            name='factorvalue',
            unique_together=set([('csrv', 'fact')]),
        ),
    ]