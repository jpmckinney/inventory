# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='source_url',
            field=models.URLField(max_length=500, unique=True),
            preserve_default=True,
        ),
    ]
