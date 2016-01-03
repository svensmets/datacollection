# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchTask',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('task', models.CharField(max_length=250, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TwitterList',
            fields=[
                ('list_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('list_name', models.CharField(max_length=200)),
                ('list_full_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TwitterUser',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('screen_name', models.CharField(max_length=100)),
                ('friends_count', models.BigIntegerField()),
                ('followers_count', models.BigIntegerField()),
                ('is_protected', models.BooleanField(default=False)),
                ('max_followers_exceeded', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='twitterlist',
            name='user_membership',
            field=models.ManyToManyField(related_name='list_membership', blank=True, to='twitter.TwitterUser'),
        ),
        migrations.AddField(
            model_name='twitterlist',
            name='user_subscription',
            field=models.ManyToManyField(related_name='list_subscription', blank=True, to='twitter.TwitterUser'),
        ),
    ]
