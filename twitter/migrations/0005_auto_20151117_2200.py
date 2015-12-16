# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0004_auto_20151117_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchtask',
            name='task',
            field=models.CharField(null=True, max_length=250),
        ),
    ]
