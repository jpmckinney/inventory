# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20141025_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='license',
            field=models.URLField(db_index=True, default=''),
            preserve_default=True,
        ),
    ]
