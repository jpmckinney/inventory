# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_distribution_validation_extension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distribution',
            name='country_code',
            field=models.CharField(max_length=3, db_index=True),
            preserve_default=True,
        ),
    ]
