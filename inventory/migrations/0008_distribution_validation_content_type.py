# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20141107_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='distribution',
            name='validation_content_type',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]