# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_auto_20150109_1754'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='country_code',
            new_name='division_id',
        ),
        migrations.RenameField(
            model_name='distribution',
            old_name='country_code',
            new_name='division_id',
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together=set([('division_id', 'name')]),
        ),
    ]
