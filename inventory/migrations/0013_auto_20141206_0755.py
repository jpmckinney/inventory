# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distribution',
            name='validation_errors',
            field=djorm_pgarray.fields.ArrayField(dbtype='text'),
            preserve_default=True,
        ),
    ]
