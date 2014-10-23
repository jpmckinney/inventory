# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20141023_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='_id',
            field=uuidfield.fields.UUIDField(max_length=32),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('package', '_id')]),
        ),
    ]
