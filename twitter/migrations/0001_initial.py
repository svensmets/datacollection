# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TwitterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('user_id', models.BigIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('screen_name', models.CharField(max_length=100)),
                ('friends_count', models.BigIntegerField()),
                ('followers_count', models.BigIntegerField()),
                ('is_protected', models.BooleanField(default=False)),
                ('max_followers_exceeded', models.BooleanField(default=False)),
            ],
        ),
    ]
