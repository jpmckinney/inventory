# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20141023_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='size',
            field=models.BigIntegerField(null=True),
            preserve_default=True,
        ),
    ]
