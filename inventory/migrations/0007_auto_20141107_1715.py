# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20141106_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='distribution',
            name='valid',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distribution',
            name='validation_encoding',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distribution',
            name='validation_errors',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='distribution',
            name='validation_headers',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
