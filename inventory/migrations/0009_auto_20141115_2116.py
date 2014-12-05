# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_distribution_validation_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='accrualPeriodicity',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='language',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='spatial',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distribution',
            name='license',
            field=models.URLField(default='', db_index=True),
            preserve_default=True,
        ),
    ]
