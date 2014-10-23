# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20141023_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='_id',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
