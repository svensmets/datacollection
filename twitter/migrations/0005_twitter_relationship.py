# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0004_auto_20151227_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Twitter_Relationship',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('from_user_id', models.BigIntegerField()),
                ('to_user_id', models.BigIntegerField()),
                ('relation_used', models.CharField(max_length=100)),
            ],
        ),
    ]
