# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20150217_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='distribution',
            name='http_status_code',
            field=models.SmallIntegerField(null=True),
            preserve_default=True,
        ),
    ]
