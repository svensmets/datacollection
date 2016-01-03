# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0003_twitterkeys'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='task_id',
            field=models.CharField(default='xxxxxxx', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='twitterlist',
            name='task_id',
            field=models.CharField(default='xxxxxx', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='task_id',
            field=models.CharField(default='xxxxxxx', max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='twitterkeys',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
