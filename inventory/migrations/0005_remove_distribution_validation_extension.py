# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20150217_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distribution',
            name='validation_extension',
        ),
    ]
