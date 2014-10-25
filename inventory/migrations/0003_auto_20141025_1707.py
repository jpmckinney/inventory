# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20141025_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='modified',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
