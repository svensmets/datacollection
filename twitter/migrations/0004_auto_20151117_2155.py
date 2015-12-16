# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0003_auto_20151117_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchtask',
            name='task',
            field=models.UUIDField(null=True),
        ),
    ]
