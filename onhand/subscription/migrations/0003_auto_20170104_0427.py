# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-04 09:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_subscriptionuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionuser',
            name='subu_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
