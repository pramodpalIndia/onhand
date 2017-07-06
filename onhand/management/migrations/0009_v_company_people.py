# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-09 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_auto_20170105_0539'),
    ]

    operations = [
        migrations.CreateModel(
            name='v_company_people',
            fields=[
                ('comp_name', models.CharField(db_column='comp_name', max_length=30, verbose_name='name')),
                ('comp_phone', models.CharField(blank=True, db_column='comp_phone', max_length=20, null=True, verbose_name='phone')),
                ('comp_email', models.CharField(blank=True, db_column='comp_email', max_length=40, null=True, verbose_name='email')),
                ('comp_website', models.CharField(blank=True, db_column='comp_website', max_length=60, null=True, verbose_name='website')),
                ('cprs_id', models.IntegerField(db_column='cprs_id', primary_key=True, serialize=False, verbose_name='companyperson')),
                ('prsn_name', models.CharField(db_column='prsn_name', max_length=41, verbose_name='Name')),
                ('prsn_fname', models.CharField(db_column='prsn_fname', max_length=20, verbose_name='First name')),
                ('prsn_lname', models.CharField(db_column='prsn_lname', max_length=20, verbose_name='Last name')),
                ('mobile_phone', models.CharField(blank=True, db_column='prsn_mobile_phone', max_length=20, null=True, verbose_name='mobile phone')),
                ('office_phone', models.CharField(blank=True, db_column='prsn_office_phone', max_length=20, null=True, verbose_name='office phone')),
                ('email', models.CharField(blank=True, db_column='prsn_email', max_length=60, null=True, verbose_name='email')),
            ],
            options={
                'db_table': 'v_company_people',
                'verbose_name': 'v_company_people',
                'verbose_name_plural': 'v_company_people',
                'managed': False,
            },
        ),
    ]