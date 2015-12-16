# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0002_auto_20151117_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchtask',
            name='task',
            field=models.ForeignKey(to='djcelery.TaskState', null=True),
        ),
        migrations.AlterField(
            model_name='searchtask',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
