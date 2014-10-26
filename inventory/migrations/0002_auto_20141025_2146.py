# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='country_code',
            field=models.CharField(max_length=2, db_index=True),
            preserve_default=True,
        ),
    ]
