# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchtask',
            name='task',
            field=models.CharField(null=True, max_length=10),
        ),
        migrations.AddField(
            model_name='searchtask',
            name='user',
            field=models.CharField(null=True, max_length=10),
        ),
    ]
