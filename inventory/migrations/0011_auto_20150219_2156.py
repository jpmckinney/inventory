# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_auto_20150219_2142'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='distribution',
            index_together=set([('dataset', 'mediaType'), ('dataset', 'division_id', 'mediaType')]),
        ),
    ]
