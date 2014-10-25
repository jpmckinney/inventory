# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='issued',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
