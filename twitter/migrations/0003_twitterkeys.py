# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0002_tweet'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterKeys',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('consumer_key', models.CharField(max_length=200)),
                ('consumer_secret', models.CharField(max_length=200)),
                ('access_token', models.CharField(max_length=200)),
                ('access_token_secret', models.CharField(max_length=200)),
                ('user', models.ForeignKey(to='twitter.TwitterUser')),
            ],
        ),
    ]
