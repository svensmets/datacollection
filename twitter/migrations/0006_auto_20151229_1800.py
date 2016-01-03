# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0005_twitter_relationship'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Twitter_Relationship',
            new_name='TwitterRelationship',
        ),
    ]
