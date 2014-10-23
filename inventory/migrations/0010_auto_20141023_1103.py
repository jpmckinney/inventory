# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_auto_20141023_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='url',
            field=models.URLField(default='', max_length=2000),
            preserve_default=True,
        ),
    ]
