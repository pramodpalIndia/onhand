# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-28 02:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('management', '0002_auto_20161213_1934'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLevel',
            fields=[
                ('accs_code', models.CharField(max_length=1, primary_key=True, serialize=False, verbose_name='Access')),
                ('accs_desc', models.CharField(max_length=20, verbose_name='description')),
            ],
            options={
                'verbose_name_plural': 'access_levels',
                'db_table': 'oh_access_level',
                'verbose_name': 'access_level',
            },
        ),
        migrations.CreateModel(
            name='FunctionRoleAccessLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accs_code', models.ForeignKey(db_column='accs_code', on_delete=django.db.models.deletion.DO_NOTHING, to='ohauth.AccessLevel', verbose_name='Access')),
            ],
            options={
                'verbose_name_plural': 'function_role_access_levels',
                'db_table': 'oh_function_role_access_level',
                'verbose_name': 'function_role_access_level',
            },
        ),
        migrations.CreateModel(
            name='OhFunction',
            fields=[
                ('func_id', models.AutoField(db_column='func_id', primary_key=True, serialize=False, verbose_name='function')),
                ('func_name', models.CharField(db_column='func_name', max_length=60, verbose_name='description')),
            ],
            options={
                'verbose_name_plural': 'oh_functions',
                'db_table': 'oh_function',
                'verbose_name': 'oh_function',
            },
        ),
        migrations.AddField(
            model_name='functionroleaccesslevel',
            name='func',
            field=models.ForeignKey(db_column='func_id', on_delete=django.db.models.deletion.DO_NOTHING, to='ohauth.OhFunction', verbose_name='Function'),
        ),
        migrations.AddField(
            model_name='functionroleaccesslevel',
            name='role_code',
            field=models.ForeignKey(db_column='role_code', on_delete=django.db.models.deletion.DO_NOTHING, to='management.Role', verbose_name='Role'),
        ),
        migrations.AlterUniqueTogether(
            name='functionroleaccesslevel',
            unique_together=set([('func', 'role_code', 'accs_code')]),
        ),
    ]
