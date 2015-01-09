# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_auto_20141124_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='country_code',
            field=models.CharField(db_index=True, max_length=3),
            preserve_default=True,
        ),
    ]
