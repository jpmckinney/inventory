# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_auto_20141115_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='distribution',
            name='validation_extension',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
