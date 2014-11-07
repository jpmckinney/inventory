# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20141106_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='temporary_keyword',
            field=djorm_pgarray.fields.ArrayField(dbtype='text'),
            preserve_default=True,
        ),
    ]
