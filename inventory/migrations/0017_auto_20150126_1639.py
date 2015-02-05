# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_auto_20150126_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='division_id',
            field=models.CharField(db_index=True, max_length=150),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='distribution',
            name='division_id',
            field=models.CharField(db_index=True, max_length=150),
            preserve_default=True,
        ),
    ]
