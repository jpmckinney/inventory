# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_distribution_validation_extension'),
    ]

    operations = [
        migrations.RenameField(
            model_name='distribution',
            old_name='validation_errors',
            new_name='errors',
        ),
        migrations.RenameField(
            model_name='distribution',
            old_name='validation_encoding',
            new_name='http_charset',
        ),
        migrations.RenameField(
            model_name='distribution',
            old_name='validation_content_type',
            new_name='http_content_type',
        ),
        migrations.RenameField(
            model_name='distribution',
            old_name='validation_headers',
            new_name='http_headers',
        ),
        migrations.AddField(
            model_name='distribution',
            name='http_content_length',
            field=models.BigIntegerField(null=True),
            preserve_default=True,
        ),
    ]
