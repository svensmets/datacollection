# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('tweet_id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('tweeter_id', models.BigIntegerField()),
                ('tweeter_name', models.CharField(max_length=200)),
                ('tweet_text', models.CharField(max_length=200)),
                ('tweet_date', models.DateTimeField()),
                ('is_retweet', models.BooleanField()),
                ('mentions', models.CharField(max_length=200, blank=True)),
                ('hashtags', models.CharField(max_length=200, blank=True)),
                ('hyperlinks', models.CharField(max_length=200, blank=True)),
            ],
        ),
    ]
