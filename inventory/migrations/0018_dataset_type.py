# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_auto_20150126_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='type',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
