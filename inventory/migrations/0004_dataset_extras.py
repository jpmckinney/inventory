# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_dataset_license'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='extras',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=True,
        ),
    ]
