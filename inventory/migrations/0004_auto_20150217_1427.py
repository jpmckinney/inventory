# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20150215_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distribution',
            name='validation_content_type',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='distribution',
            name='validation_encoding',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='distribution',
            name='validation_extension',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='distribution',
            name='validation_headers',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=True,
        ),
    ]
